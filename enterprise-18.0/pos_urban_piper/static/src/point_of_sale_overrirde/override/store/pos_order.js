import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(vals);
        this.isDeliveryRefundOrder = false;
    },

    get_delivery_provider_name() {
        return this.delivery_provider_id ? this.delivery_provider_id.name : "";
    },

    get_order_status() {
        return this.delivery_status ? this.delivery_status : "";
    },

    export_for_printing(baseUrl, headerData) {
        const data = super.export_for_printing(baseUrl, headerData);
        data.headerData.deliveryId = this.delivery_identifier;
        data.headerData.deliveryChannel = this.delivery_provider_id?.name;
        return data;
    },
});
