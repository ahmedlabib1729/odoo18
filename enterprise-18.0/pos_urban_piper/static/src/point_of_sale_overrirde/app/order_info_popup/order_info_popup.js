import { Dialog } from "@web/core/dialog/dialog";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { user } from "@web/core/user";

export class orderInfoPopup extends Component {
    static components = { Dialog };
    static template = "pos_urban_piper.orderInfoPopup";
    static props = {
        order: Object,
        order_status: Object,
        close: Function,
    };

    setup() {
        this.pos = usePos();
        this.deliveryJson = JSON.parse(this.props.order.delivery_json);
        this.extPlatform = this.deliveryJson?.order?.details?.ext_platforms?.[0];
        this.store = this.deliveryJson?.order?.store;
        this.deliveryRiderJson = JSON.parse(this.props.order.delivery_rider_json);
    }
    /**
     * This method converts time from milliseconds to the user's time zone.
     */
    getTime(time) {
        const formattedTime = Intl.DateTimeFormat("en-US", {
            timeZone: user.tz || luxon.Settings.defaultZone.name,
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        }).format(time);
        return formattedTime;
    }

    onClose() {
        this.props.close();
    }

    getOrderDetails() {
        return {
            channelOtp: this.extPlatform?.id,
            orderOtp: this.extPlatform?.extras?.order_otp,
            fulfilmentMode: this.extPlatform?.delivery_type,
            outletName: this.store?.name,
        };
    }
}
