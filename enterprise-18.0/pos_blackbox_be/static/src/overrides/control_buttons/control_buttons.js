import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { onWillStart, useState } from "@odoo/owl";

patch(ControlButtons.prototype, {
    setup() {
        this.pos = usePos();
        this.printer = useService("printer");
        this.state = useState({
            status: false,
            buttonDisabled: false,
        });

        onWillStart(async () => {
            this.state.status = await this.getUserSessionStatus();
        });
    },
    async getUserSessionStatus() {
        let cashier = this.pos.get_cashier();

        if (cashier.model.pythonModel === "hr.employee") {
            cashier = this.pos.user.id;
        }

        return await this.pos.data.call(
            "pos.session",
            "get_user_session_work_status",
            [this.pos.session.id],
            {
                user_id: cashier.id,
            }
        );
    },
    async setUserSessionStatus(status) {
        let cashier = this.pos.get_cashier();

        if (cashier.model.pythonModel === "hr.employee") {
            cashier = this.pos.user.id;
        }

        const users = await this.pos.data.call(
            "pos.session",
            "set_user_session_work_status",
            [this.pos.session.id],
            {
                user_id: cashier,
                status: status,
            }
        );
        if (this.pos.config.module_pos_hr) {
            this.pos.session.employees_clocked_ids = users;
        } else {
            this.pos.session.users_clocked_ids = users;
        }
    },
    async clickWorkButton() {
        if (this.pos.get_order().orderlines.length) {
            this.pos.env.services.dialog.add(AlertDialog, {
                title: _t("Fiscal Data Module error"),
                body: _t("Cannot clock in/out if the order is not empty"),
            });
            return;
        }
        const clocked = await this.getUserSessionStatus();

        this.state.buttonDisabled = true;
        if (!this.state.status && !clocked) {
            await this.ClockIn();
        }
        if (this.state.status && clocked) {
            await this.ClockOut();
        }
        this.state.buttonDisabled = false;
    },
    async ClockIn() {
        try {
            await this.createOrderForClocking();
            await this.setUserSessionStatus(true);
            this.state.status = true;
        } catch (err) {
            console.error(err);
        }
    },
    async ClockOut() {
        await this.createOrderForClocking();
        await this.setUserSessionStatus(false);
        this.state.status = false;
    },
    async createOrderForClocking() {
        const order = this.pos.get_order();
        order.add_product(this.state.status ? this.pos.workOutProduct : this.pos.workInProduct, {
            force: true,
        });
        order.draft = false;
        order.clock = this.state.status ? "out" : "in";

        await this.pos.push_single_order(order);
        await this.printer.print(OrderReceipt, {
            data: this.pos.orderExportForPrinting(order),
            formatCurrency: this.env.utils.formatCurrency,
        });

        if (this.pos.config.module_pos_restaurant) {
            this.pos.showScreen("FloorScreen");
        } else {
            this.pos.add_new_order();
            this.pos.showScreen("ProductScreen");
        }
    },
    clickRefund() {
        if (this.pos.useBlackBoxBe() && !this.pos.checkIfUserClocked()) {
            this.pos.env.services.dialog.add(AlertDialog, {
                title: this._t("POS error"),
                body: this._t("User must be clocked in."),
            });
            return;
        }
        super.clickRefund();
    },
    async clickPrintBill() {
        const order = this.pos.get_order();
        if (this.pos.useBlackBoxBe() && order.get_orderlines().length > 0) {
            await this.pos.pushProFormaOrder(order);
        }
        await super.clickPrintBill();
    },
});
