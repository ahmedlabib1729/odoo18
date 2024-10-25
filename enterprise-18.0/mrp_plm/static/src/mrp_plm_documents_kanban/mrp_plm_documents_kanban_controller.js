/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductDocumentKanbanController } from "@product/js/product_document_kanban/product_document_kanban_controller";

patch(ProductDocumentKanbanController.prototype, {
    buildFormData(formData) {
        super.buildFormData(formData);
        if (this.props.context.eco_bom) {
            formData.append("eco_bom", true);
        }
    },
});
