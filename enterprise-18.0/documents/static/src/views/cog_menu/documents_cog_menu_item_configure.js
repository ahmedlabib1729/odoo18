import { STATIC_COG_GROUP_ACTION_ADVANCED } from "./documents_cog_menu_group";
import { DocumentsCogMenuItem } from "./documents_cog_menu_item";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class DocumentsCogMenuItemConfigure extends DocumentsCogMenuItem {
    setup() {
        this.icon = "fa-edit";
        this.label = _t("Configure");
        super.setup();
        this.action = useService("action");
    }

    async doActionOnFolder(folder) {
        this.env.documentsView.bus.trigger("documents-close-preview");
        return this.action.doAction(
            {
                res_model: "documents.document",
                res_id: folder.id,
                name: _t("Edit"),
                type: "ir.actions.act_window",
                target: "new",
                views: [[false, "form"]],
                context: {
                    create: false,
                },
            },
            {
                onClose: () => this.env.searchModel._reloadSearchModel(true),
            }
        );
    }
}

export const documentsCogMenuItemConfigure = {
    Component: DocumentsCogMenuItemConfigure,
    groupNumber: STATIC_COG_GROUP_ACTION_ADVANCED,
    isDisplayed: (env) =>
        DocumentsCogMenuItem.isVisible(env, ({ folder, documentService }) =>
            documentService.isEditable(folder)
        ),
};
