import { patch } from "@web/core/utils/patch";
import { BarcodeReader } from "@point_of_sale/app/barcode/barcode_reader_service";
import { user } from "@web/core/user";

patch(BarcodeReader.prototype, {
    async showNotFoundNotification(code) {
        const response = await this.orm.call("product.template", "barcode_lookup", []);
        if ((await user.hasGroup("base.group_system")) && response?.authenticated) {
            this.action.doAction("point_of_sale.product_product_action_add_pos", {
                additionalContext: {
                    default_barcode: code.code,
                },
            });
            this.hardwareProxy.pos.scanning = false;
            return true;
        }
        return super.showNotFoundNotification(code);
    },
});
