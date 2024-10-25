/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ListRenderer } from "@web/views/list/list_renderer";

import { useService, useBus } from "@web/core/utils/hooks";
import { FileUploadProgressContainer } from "@web/core/file_upload/file_upload_progress_container";
import { FileUploadProgressDataRow } from "@web/core/file_upload/file_upload_progress_record";
import { DocumentsDropZone } from "../helper/documents_drop_zone";
import { DocumentsActionHelper } from "../helper/documents_action_helper";
import { DocumentsFileViewer } from "../helper/documents_file_viewer";
import { DocumentsListRendererCheckBox } from "./documents_list_renderer_checkbox";
import { useCommand } from "@web/core/commands/command_hook";
import { useRef, useState } from "@odoo/owl";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { Chatter } from "@mail/chatter/web_portal/chatter";

export class DocumentsListRenderer extends ListRenderer {
    static props = [...ListRenderer.props, "previewStore"];
    static template = "documents.DocumentsListRenderer";
    static recordRowTemplate = "documents.DocumentsListRenderer.RecordRow";
    static components = Object.assign({}, ListRenderer.components, {
        DocumentsListRendererCheckBox,
        FileUploadProgressContainer,
        FileUploadProgressDataRow,
        DocumentsDropZone,
        DocumentsActionHelper,
        DocumentsFileViewer,
        Chatter,
    });

    setup() {
        super.setup();
        this.root = useRef("root");
        const { uploads } = useService("file_upload");
        this.documentService = useService("document.document");

        this.documentUploads = uploads;
        useCommand(
            _t("Select all"),
            () => {
                const allSelected =
                    this.props.list.selection.length === this.props.list.records.length;
                this.props.list.records.forEach((record) => {
                    record.toggleSelection(!allSelected);
                });
            },
            {
                category: "smart_action",
                hotkey: "control+a",
            }
        );

        // TODO: clean that crap
        this.chatterState = useState({ visible: this.documentService.isChatterVisible() });
        useBus(this.env.documentsView.bus, "documents-toggle-chatter", (event) => {
            this.chatterState.visible = !this.chatterState.visible;
            this.documentService.setChatterVisible(this.chatterState.visible);
        });
        useBus(this.documentService.bus, "DOCUMENT_PREVIEWED", async (ev) => {
            this.chatterState.previewedDocument = this.documentService.previewedDocument;
        });
    }

    getDocumentsAttachmentViewerProps() {
        return { previewStore: this.props.previewStore };
    }

    /**
     * Called when a keydown event is triggered.
     */
    onGlobalKeydown(ev) {
        if (ev.key !== "Enter" && ev.key !== " ") {
            return;
        }
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (!record) {
            return;
        }
        const options = {};
        if (ev.key === "Enter") {
            if (record.data.type === "folder") {
                record.onRecordDoubleClick();
            } else {
                record.onClickPreview(ev);
            }
        } else if (ev.key === " ") {
            options.isKeepSelection = true;
        }
        ev.stopPropagation();
        ev.preventDefault();
        record.onRecordClick(ev, options);
    }

    /**
     * There's a custom behavior on cell clicked as we (un)select the row (see record.onRecordClick)
     */
    onCellClicked(record, column, ev) {
        if (record.selected && this.editableColumns.includes(column.name)) {
            return super.onCellClicked(...arguments);
        }
    }
    get editableColumns() {
        return ["name", "tag_ids", "partner_id", "owner_id", "company_id"];
    }

    onCellDoubleClick(ev) {
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (record.data.type !== "folder") {
            ev.stopPropagation();
            record.onClickPreview(ev);
            return;
        }
        record.onRecordDoubleClick();
    }

    /**
     * Called when a click event is triggered.
     */
    onGlobalClick(ev) {
        // We have to check that we are indeed clicking in the list view as on mobile,
        // the inspector renders above the renderer but it still triggers this event.
        if (ev.target.closest(".o_data_row") || !ev.target.closest(".o_list_renderer")) {
            return;
        }
        this.props.list.selection.forEach((el) => el.toggleSelection(false));
    }

    onCellKeydown(ev, group = null, record = null) {
        const hotkey = getActiveHotkey(ev);
        if (hotkey === "enter") {
            return;
        }
        return super.onCellKeydown(...arguments);
    }

    get hasSelectors() {
        return this.props.allowSelectors;
    }

    get isMobile() {
        return this.env.isSmall;
    }

    /**
     * Records on which we will execute the actions / see the chatter.
     */
    get targetRecords() {
        return this.chatterState.previewedDocument
            ? [this.chatterState.previewedDocument.record]
            : this.props.list.selection;
    }

    onDragEnter(ev) {
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (record.data.type !== "folder") {
            return;
        }
        if (record.selected) {
            row.classList.remove("table-info");
        }
        const isInvalidFolder = this.props.list.selection
            .map((r) => r.data.id)
            .includes(record.data.id);
        row.classList.add(isInvalidFolder ? "table-danger" : "table-success");
    }

    onDragLeave(ev) {
        const row = ev.target.closest(".o_data_row");
        // we do this since the dragleave event is fired when hovering a child
        const elemBounding = row.getBoundingClientRect();
        const isOutside =
            ev.clientX < elemBounding.left ||
            ev.clientX > elemBounding.right ||
            ev.clientY < elemBounding.top ||
            ev.clientY > elemBounding.bottom;
        if (!isOutside) {
            return;
        }
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (record.data.type !== "folder") {
            return;
        }
        if (record.selected) {
            row.classList.add("table-info");
        }
        row.classList.remove("table-success", "table-danger");
    }

    onDragOver(ev) {
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        const isInvalidTarget =
            record.data.type !== "folder" ||
            this.props.list.selection.map((r) => r.data.id).includes(record.data.id);
        const dropEffect = isInvalidTarget ? "none" : ev.ctrlKey ? "link" : "move";
        ev.dataTransfer.dropEffect = dropEffect;
    }

    onDrop(ev) {
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (record.data.type !== "folder") {
            return;
        }
        row.classList.remove("table-success", "table-danger");
        record.onDrop(ev);
    }
}
