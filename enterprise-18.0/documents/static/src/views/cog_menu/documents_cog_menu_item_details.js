import { STATIC_COG_GROUP_ACTION_ADVANCED } from "./documents_cog_menu_group";
import { DocumentsCogMenuItem } from "./documents_cog_menu_item";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class DocumentsCogMenuItemDetails extends DocumentsCogMenuItem {
    setup() {
        this.icon = "fa-info-circle";
        this.label = _t("Details");
        super.setup();
        this.documentService = useService("document.document");
    }

    async doActionOnFolder(folder) {
        await this.documentService.openDialogDetails(
            folder.id,
            this.documentService.isEditable(folder)
        );
        await this.reload();
    }
}

export const documentsCogMenuItemDetails = {
    Component: DocumentsCogMenuItemDetails,
    groupNumber: STATIC_COG_GROUP_ACTION_ADVANCED,
    isDisplayed: (env) =>
        DocumentsCogMenuItem.isVisible(env, ({ folder }) => typeof folder.id === "number"),
};
