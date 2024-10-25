import { orderInfoPopup } from "@pos_urban_piper/point_of_sale_overrirde/app/order_info_popup/order_info_popup";
import { patch } from "@web/core/utils/patch";

patch(orderInfoPopup.prototype, {
    getOrderDetails() {
        const orderDetails = super.getOrderDetails();
        if (this.props?.order?.delivery_provider_id.technical_name === "ubereats") {
            orderDetails["ubereatsCode"] = this.extPlatform?.extras?.ubereats_rider_mask_code;
            orderDetails["riderMaskCode"] = this.extPlatform?.extras?.contact_access_code;
        }
        return orderDetails;
    },
});
