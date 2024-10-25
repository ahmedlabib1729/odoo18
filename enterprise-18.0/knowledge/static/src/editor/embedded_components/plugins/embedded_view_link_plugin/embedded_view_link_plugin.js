import { Plugin } from "@html_editor/plugin";
import { boundariesOut } from "@html_editor/utils/position";
import { EMBEDDED_COMPONENT_PLUGINS } from "@html_editor/plugin_sets";
import { _t } from "@web/core/l10n/translation";

export class EmbeddedViewLinkPlugin extends Plugin {
    static name = "embeddedViewLink";
    static dependencies = ["dom", "selection"];

    handleCommand(command, payload) {
        switch (command) {
            case "SETUP_NEW_COMPONENT":
                this.setupNewComponent(payload);
                break;
        }
    }

    setupNewComponent({ name, props }) {
        if (name === "viewLink") {
            Object.assign(props, {
                removeViewLink: (text) => {
                    this.replaceElementWith(props.host, text);
                    this.dispatch("ADD_STEP");
                },
                copyViewLink: () => {
                    const cursors = this.shared.preserveSelection();
                    this.copyElementToClipboard(props.host);
                    cursors?.restore();
                },
            });
        }
    }

    replaceElementWith(target, element) {
        const [anchorNode, anchorOffset, focusNode, focusOffset] = boundariesOut(target);
        this.shared.setSelection({ anchorNode, anchorOffset, focusNode, focusOffset });
        this.shared.domInsert(element);
    }

    copyElementToClipboard(element) {
        const range = document.createRange();
        range.selectNode(element);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        const copySucceeded = document.execCommand("copy");
        selection.removeAllRanges();
        if (copySucceeded) {
            this.services.notification.add(_t("Link copied to clipboard."), {
                type: "success",
            });
        }
    }
}

EMBEDDED_COMPONENT_PLUGINS.push(EmbeddedViewLinkPlugin);
