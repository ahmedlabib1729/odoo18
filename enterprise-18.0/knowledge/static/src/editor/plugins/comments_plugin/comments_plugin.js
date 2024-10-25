import { Plugin } from "@html_editor/plugin";
import { leftPos, rightPos, nodeSize } from "@html_editor/utils/position";
import { renderToElement } from "@web/core/utils/render";
import { CommentBeaconManager } from "@knowledge/comments/comment_beacon_manager";
import { registry } from "@web/core/registry";
import { KnowledgeCommentsHandler } from "@knowledge/comments/comments_handler/comments_handler";
import { _t } from "@web/core/l10n/translation";
import { closestElement, childNodes } from "@html_editor/utils/dom_traversal";
import { callbacksForCursorUpdate } from "@html_editor/utils/selection";
import { fillEmpty } from "@html_editor/utils/dom";
import {
    paragraphRelatedElements,
    phrasingContent,
    isContentEditable,
    isZwnbsp,
} from "@html_editor/utils/dom_info";
import { uniqueId } from "@web/core/utils/functions";
import { effect } from "@web/core/utils/reactive";
import { batched } from "@web/core/utils/timing";
import { withSequence } from "@html_editor/utils/resource";

const ALLOWED_BEACON_POSITION = new Set([...paragraphRelatedElements, ...phrasingContent]);

export class KnowledgeCommentsPlugin extends Plugin {
    static name = "knowledgeComments";
    static dependencies = [
        "dom",
        "protected_node",
        "selection",
        "local-overlay",
        "position",
        "link_selection",
        "collaboration",
        "format",
    ];
    resources = {
        toolbarCategory: [
            withSequence(60, {
                id: "knowledge",
            }),
            withSequence(60, {
                id: "knowledge_image",
                namespace: "image",
            }),
        ],
        toolbarItems: [
            {
                id: "comments",
                category: "knowledge",
                action(dispatch) {
                    dispatch("ADD_COMMENTS");
                },
                icon: "fa-commenting",
                title: _t("Add a comment to selection"),
                text: _t("Comment"),
            },
            {
                id: "comments_image",
                category: "knowledge_image",
                action(dispatch) {
                    dispatch("ADD_COMMENTS");
                },
                icon: "fa-commenting",
                title: _t("Add a comment to an image"),
                text: _t("Comment"),
            },
        ],
        layoutGeometryChange: () => {
            // TODO ABD: why is this called
            this.commentBeaconManager?.drawThreadOverlays();
            this.config.onLayoutGeometryChange();
        },
        onSelectionChange: (selectionData) => {
            if (
                !selectionData.documentSelectionIsInEditable ||
                !selectionData.editableSelection ||
                selectionData.documentSelectionIsProtected ||
                selectionData.documentSelectionIsProtecting
            ) {
                return;
            }
            const editableSelection = selectionData.editableSelection;
            const target =
                editableSelection.anchorNode.nodeType === Node.TEXT_NODE
                    ? editableSelection.anchorNode
                    : childNodes(editableSelection.anchorNode).at(editableSelection.anchorOffset);
            if (!target || !target.isConnected) {
                return;
            }
            this.commentBeaconManager.activateRelatedThread(target);
        },
        // TODO ABD: arbitrary sequence, investigate what makes sense
        handle_delete_forward: withSequence(1, this.handleDeleteForward.bind(this)),
        handle_delete_backward: withSequence(1, this.handleDeleteBackward.bind(this)),
        arrows_should_skip: this.arrowShouldSkip.bind(this),
    };

    setup() {
        this.peerId = this.config.collaboration.peerId;
        this.commentsService = this.services["knowledge.comments"];
        this.commentsState = this.commentsService.getCommentsState();
        // reset pending beacons
        let previousActiveThreadId;
        this.alive = true;
        effect(
            batched((state) => {
                if (!this.alive) {
                    return;
                }
                if (previousActiveThreadId === state.activeThreadId) {
                    return;
                }
                if (
                    previousActiveThreadId !== "undefined" &&
                    state.activeThreadId === "undefined"
                ) {
                    this.commentBeaconManager.pendingBeacons = new Set();
                } else if (previousActiveThreadId === "undefined") {
                    this.commentBeaconManager.sortThreads();
                    if (this.commentBeaconManager.bogusBeacons.size) {
                        this.commentBeaconManager.removeBogusBeacons();
                        this.dispatch("ADD_STEP");
                    }
                    this.commentBeaconManager.drawThreadOverlays();
                }
                previousActiveThreadId = state.activeThreadId;
            }),
            [this.commentsState]
        );
        this.localOverlay = this.shared.makeLocalOverlay("KnowledgeThreadBeacons");
        this.commentBeaconManager = new CommentBeaconManager({
            document: this.document,
            source: this.editable,
            overlayContainer: this.localOverlay,
            commentsState: this.commentsState,
            peerId: this.peerId,
            removeBeacon: this.removeBeacon.bind(this),
            setSelection: this.shared.setSelection,
            onStep: () => {
                this.dispatch("ADD_STEP");
            },
        });
        this.addDomListener(window, "click", this.onWindowClick.bind(this));
        this.overlayComponentsKey = uniqueId("KnowledgeCommentsHandler");
        registry.category(this.config.localOverlayContainers.key).add(
            this.overlayComponentsKey,
            {
                Component: KnowledgeCommentsHandler,
                props: {
                    commentBeaconManager: this.commentBeaconManager,
                    contentRef: {
                        el: this.editable,
                    },
                },
            },
            { force: true }
        );
    }

    handleCommand(command, payload) {
        switch (command) {
            case "ADD_COMMENTS":
                this.addCommentToSelection();
                break;
            case "NORMALIZE":
                this.normalize(payload.node);
                break;
            case "RESTORE_SAVEPOINT":
            case "ADD_EXTERNAL_STEP":
            case "HISTORY_RESET_FROM_STEPS":
            case "HISTORY_RESET":
                this.updateBeacons();
                break;
            case "STEP_ADDED":
                this.commentBeaconManager.drawThreadOverlays();
                break;
            case "CLEAN_FOR_SAVE":
                this.cleanForSave(payload.root);
                break;
        }
    }

    arrowShouldSkip(ev, char, lastSkipped) {
        if (char !== undefined || lastSkipped !== "\uFEFF") {
            return;
        }
        const selection = this.document.getSelection();
        if (!selection) {
            return;
        }
        const { anchorNode, focusNode } = selection;
        if (
            !this.editable.contains(anchorNode) ||
            (focusNode !== anchorNode && !this.editable.contains(focusNode))
        ) {
            return;
        }
        const screenDirection = ev.key === "ArrowLeft" ? "left" : "right";
        const isRtl = closestElement(focusNode, "[dir]")?.dir === "rtl";
        const domDirection = (screenDirection === "left") ^ isRtl ? "previous" : "next";
        let targetNode;
        let targetOffset;
        const range = selection.getRangeAt(0);
        if (ev.shiftKey) {
            targetNode = selection.focusNode;
            targetOffset = selection.focusOffset;
        } else {
            if (domDirection === "previous") {
                targetNode = range.startContainer;
                targetOffset = range.startOffset;
            } else {
                targetNode = range.endContainer;
                targetOffset = range.endOffset;
            }
        }
        if (domDirection === "previous") {
            const beacon = this.identifyPreviousBeacon({
                endContainer: targetNode,
                endOffset: targetOffset,
            });
            return beacon && this.commentBeaconManager.isDisabled(beacon);
        } else {
            const beacon = this.identifyNextBeacon({
                startContainer: targetNode,
                startOffset: targetOffset,
            });
            return beacon && this.commentBeaconManager.isDisabled(beacon);
        }
    }

    identifyNextBeacon(range) {
        const { startContainer, startOffset } = range;
        if (startContainer.nodeType !== Node.TEXT_NODE) {
            return;
        }
        let container;
        if (isZwnbsp(startContainer)) {
            container = startContainer;
        } else if (
            startOffset === nodeSize(startContainer) &&
            startContainer.nextSibling?.nodeType === Node.TEXT_NODE &&
            isZwnbsp(startContainer.nextSibling)
        ) {
            container = startContainer.nextSibling;
        }
        if (container) {
            const [anchorNode, anchorOffset] = rightPos(container);
            const target = childNodes(anchorNode).at(anchorOffset);
            if (target?.matches?.(".oe_thread_beacon")) {
                return target;
            }
        }
    }

    identifyPreviousBeacon(range) {
        const { endContainer, endOffset } = range;
        if (endContainer.nodeType !== Node.TEXT_NODE) {
            return;
        }
        let container;
        if (isZwnbsp(endContainer)) {
            container = endContainer;
        } else if (
            endOffset === 0 &&
            endContainer.previousSibling?.nodeType === Node.TEXT_NODE &&
            isZwnbsp(endContainer.previousSibling)
        ) {
            // This part of the condition may not be necessary since
            // it seems that endOffset is never set at 0
            container = endContainer.previousSibling;
        }
        if (container) {
            const [anchorNode, anchorOffset] = leftPos(container);
            if (anchorOffset === 0) {
                return;
            }
            const target = childNodes(anchorNode).at(anchorOffset - 1);
            if (target?.matches?.(".oe_thread_beacon")) {
                return target;
            }
        }
    }

    // TODO ABD: -> CTRL + DELETE needs some custo too (currently deletes too much)
    handleDeleteForward(range) {
        // allow deleteForward to go past a beacon instead of being blocked.
        // TODO ABD: add tests for both cases
        const target = this.identifyNextBeacon(range);
        if (target) {
            const [anchorNode, anchorOffset] = rightPos(target);
            this.shared.setSelection({
                anchorNode,
                anchorOffset,
            });
            this.dispatch("DELETE_FORWARD");
            return true;
        }
    }

    handleDeleteBackward(range) {
        // allow deleteBackward to go past a beacon instead of being blocked.
        const target = this.identifyPreviousBeacon(range);
        if (target) {
            const [anchorNode, anchorOffset] = leftPos(target);
            this.shared.setSelection({
                anchorNode,
                anchorOffset,
            });
            this.dispatch("DELETE_BACKWARD");
            return true;
        }
    }

    addCommentToSelection() {
        // TODO ABD: can this method ever be called if either the start or the
        // end of the selection are in a non-editable positon ?
        const { startContainer, startOffset, endContainer, endOffset } =
            this.shared.getEditableSelection({ deep: true });
        const isCollapsed = startContainer === endContainer && startOffset === endOffset;
        if (
            isCollapsed ||
            !ALLOWED_BEACON_POSITION.has(startContainer.nodeName) ||
            !ALLOWED_BEACON_POSITION.has(endContainer.nodeName) ||
            !isContentEditable(startContainer) ||
            !isContentEditable(endContainer)
        ) {
            return;
        }
        const previousUndefinedBeacons = [
            ...this.editable.querySelectorAll(".oe_thread_beacon[data-id='undefined']"),
        ];
        this.commentBeaconManager.pendingBeacons = new Set();
        const endBeacon = renderToElement("knowledge.threadBeacon", {
            threadId: "undefined",
            type: "threadBeaconEnd",
            recordId: this.commentsState.articleId,
            recordModel: "knowledge.article",
            peerId: this.peerId,
        });
        this.shared.setSelection({
            anchorNode: endContainer,
            anchorOffset: endOffset,
        });
        this.commentBeaconManager.pendingBeacons.add(endBeacon);
        this.shared.domInsert(endBeacon);
        const startBeacon = renderToElement("knowledge.threadBeacon", {
            threadId: "undefined",
            type: "threadBeaconStart",
            recordId: this.commentsState.articleId,
            recordModel: "knowledge.article",
            peerId: this.peerId,
        });
        this.shared.setSelection({
            anchorNode: startContainer,
            anchorOffset: startOffset,
        });
        this.commentBeaconManager.pendingBeacons.add(startBeacon);
        this.shared.domInsert(startBeacon);
        this.commentBeaconManager.cleanupThread("undefined");
        for (const beacon of previousUndefinedBeacons) {
            this.removeBeacon(beacon);
        }
        const [anchorNode, anchorOffset] = rightPos(startBeacon);
        this.shared.setSelection({
            anchorNode,
            anchorOffset,
        });
        this.commentsState.displayMode = "handler";
        this.commentsService.createVirtualThread();
        this.commentsState.activeThreadId = "undefined";
        this.dispatch("ADD_STEP");
    }

    onWindowClick(ev) {
        const selector = ".oe-local-overlay, .o_knowledge_comment_box, .o-overlay-container";
        const closestElement = ev.target.closest(selector);
        if (!closestElement && !this.editable.contains(ev.target)) {
            this.commentsState.activeThreadId = undefined;
        }
    }

    normalize(elem) {
        this.commentBeaconManager.sortThreads();
        // TODO ABD: think about the fact that a beacon can be normalized in different steps
        // for different users, is this an issue ?
        this.commentBeaconManager.removeBogusBeacons();
        for (const beacon of elem.querySelectorAll(".oe_thread_beacon")) {
            if (beacon.isConnected && !ALLOWED_BEACON_POSITION.has(beacon.parentElement.nodeName)) {
                // TODO ABD: evaluate cleanupThread ?
                this.commentBeaconManager.cleanupBeaconPair(beacon.dataset.id);
                this.removeBeacon(beacon);
                continue;
            }
            this.shared.padLinkWithZwnbsp(beacon);
            this.shared.setProtectingNode(beacon, true);
        }
    }

    cleanZwnbsp(beacon) {
        if (!beacon.isConnected) {
            return;
        }
        const cursors = this.shared.preserveSelection();
        if (
            isZwnbsp(beacon.previousSibling) &&
            beacon.previousSibling.previousSibling?.nodeName !== "A"
        ) {
            cursors.update(callbacksForCursorUpdate.remove(beacon.previousSibling));
            beacon.previousSibling.remove();
        }
        if (isZwnbsp(beacon.nextSibling) && beacon.nextSibling.nextSibling?.nodeName !== "A") {
            cursors.update(callbacksForCursorUpdate.remove(beacon.nextSibling));
            beacon.nextSibling.remove();
        }
        cursors.restore();
    }

    removeBeacon(beacon) {
        if (!beacon.isConnected) {
            return;
        }
        this.cleanZwnbsp(beacon);
        const cursors = this.shared.preserveSelection();
        const parent = beacon.parentElement;
        cursors.update(callbacksForCursorUpdate.remove(beacon));
        beacon.remove();
        cursors.restore();
        fillEmpty(parent);
        this.shared.mergeAdjacentInlines(parent);
    }

    updateBeacons() {
        this.commentBeaconManager.sortThreads();
        this.commentBeaconManager.drawThreadOverlays();
    }

    destroy() {
        super.destroy();
        this.alive = false;
        registry.category(this.config.localOverlayContainers.key).remove(this.overlayComponentsKey);
        this.commentBeaconManager.destroy();
        this.localOverlay.remove();
    }

    cleanForSave(root) {
        const bogusIds = new Set(["undefined"]);
        for (const beacon of this.commentBeaconManager.bogusBeacons) {
            bogusIds.add(beacon.dataset.id);
        }
        for (const beacon of root.querySelectorAll(".oe_thread_beacon")) {
            if (bogusIds.has(beacon.dataset.id)) {
                beacon.remove();
            } else {
                // remove zwnbsp
                beacon.replaceChildren();
                delete beacon.dataset.peerId;
            }
        }
    }
}
