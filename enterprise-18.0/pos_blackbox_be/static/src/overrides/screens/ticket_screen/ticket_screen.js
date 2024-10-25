import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

/**
 * Prevent refunding work in/out lines.
 */
patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.numberBuffer = useService("number_buffer");
        this.notification = useService("notification");
    },
    _onUpdateSelectedOrderline({ detail }) {
        const order = this.getSelectedOrder();
        if (!order) {
            return this.numberBuffer.reset();
        }

        const selectedOrderlineId = this.getSelectedOrderlineId();
        const orderline = order.lines.find((line) => line.id == selectedOrderlineId);
        if (!orderline) {
            return this.numberBuffer.reset();
        }
        if (
            orderline.product_id.id === this.pos.workOutProduct.id ||
            orderline.product_id.id === this.pos.workInProduct.id
        ) {
            this.notification.add(_t("Refunding work in/out product is not allowed."));
            return;
        }
        super._onUpdateSelectedOrderline(...arguments);
    },
    shouldHideDeleteButton(order) {
        return this.pos.useBlackBoxBe() || super.shouldHideDeleteButton(order);
    },
});
