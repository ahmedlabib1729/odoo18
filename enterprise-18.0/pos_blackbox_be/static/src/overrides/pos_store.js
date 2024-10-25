import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

patch(PosStore.prototype, {
    async printReceipt() {
        if (this.useBlackBoxBe()) {
            await this.dialog.add(AlertDialog, {
                title: _t("Fiscal Data Module Restriction"),
                body: _t(
                    "You are not allowed to reprint a ticket when using the fiscal data module."
                ),
            });
            return;
        }

        await super.printReceipt();
    },
    async addLineToCurrentOrder(vals, opt = {}, configure = true) {
        const product = vals.product_id;
        if (this.useBlackBoxBe() && product.get_price() < 0) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t(
                    "It's forbidden to sell product with negative price when using the black box.\nPerform a refund instead."
                ),
            });
            return;
        } else if (this.useBlackBoxBe() && product.taxes_id.length === 0) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t("Product has no tax associated with it."),
            });
            return;
        } else if (
            this.useBlackBoxBe() &&
            !this.checkIfUserClocked() &&
            product !== this.config.workInProduct &&
            !opt.force
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t("User must be clocked in."),
            });
            return;
        } else if (
            this.useBlackBoxBe() &&
            this.pos.useBlackBoxBe() &&
            !product.taxes_id.every((tax) => tax?.tax_group_id.pos_receipt_label)
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t(
                    "Product has an invalid tax amount. Only 21%, 12%, 6% and 0% are allowed."
                ),
            });
            return;
        } else if (
            this.useBlackBoxBe() &&
            product.id === this.config.workInProduct.id &&
            !opt.force
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t("This product is not allowed to be sold"),
            });
            return;
        } else if (
            this.useBlackBoxBe() &&
            product.id === this.config.workOutProduct.id &&
            !opt.force
        ) {
            this.dialog.add(AlertDialog, {
                title: _t("POS error"),
                body: _t("This product is not allowed to be sold"),
            });
            return;
        }

        return await super.addLineToCurrentOrder(vals, opt, configure);
    },
    async processServerData(loadedData) {
        await super.processServerData(loadedData);

        this.config.workInProduct = this.models["product.product"].get(
            this.session._product_product_work_in
        );
        this.config.workOutProduct = this.models["product.product"].get(
            this.session._product_product_work_out
        );
        this.config.server_version = this.session._server_version;
    },
    useBlackBoxBe() {
        return this.config.iface_fiscal_data_module;
    },
    checkIfUserClocked() {
        const cashierId = this.get_cashier().id;
        if (this.config.module_pos_hr) {
            return this.session.employees_clocked_ids.find((elem) => elem === cashierId);
        }
        return this.session.users_clocked_ids.find((elem) => elem === cashierId);
    },
    disallowLineQuantityChange() {
        const result = super.disallowLineQuantityChange();
        return this.useBlackBoxBe() || result;
    },
    doNotAllowRefundAndSales() {
        const result = super.doNotAllowRefundAndSales();
        return this.useBlackBoxBe() || result;
    },
    async pushProFormaOrder(order) {
        order.receipt_type = order.get_total_with_tax() >= 0 ? "PS" : "PR";
        await this.syncAllOrders();
        await this.pushToBlackbox(order);
    },
    async pushToBlackbox(order) {
        try {
            const data = await this.pushDataToBlackbox(this.createOrderDataForBlackbox(order));
            if (data.value.error && data.value.error.errorCode != "000000") {
                throw data.value.error;
            }
            this.setDataForPushOrderFromBlackbox(order, data);
        } catch (err) {
            console.log(err);
            if (err.errorCode === "202000") {
                // need to be tested
                const { confirmed, payload } = await this.popup.add(NumberPopup, {
                    startingValue: 0,
                    title: _t("Enter pin code:"),
                });

                if (!confirmed) {
                    return;
                }
                this.pushDataToBlackbox(this.createPinCodeDataForBlackbox(payload));
            } else {
                // other errors
                this.env.services.dialog.add(AlertDialog, {
                    title: _t("Blackbox error"),
                    body: _t(err.status ? err.status : "Internal blackbox error"),
                });
                return;
            }
        }
    },
    async push_single_order(order, opts) {
        if (this.useBlackBoxBe() && order) {
            order.receipt_type = false;
            await this.pushToBlackbox(order);
        }
        return await super.push_single_order(order, opts);
    },
    createPinCodeDataForBlackbox(code) {
        return "P040" + code;
    },
    createOrderDataForBlackbox(order) {
        order.blackbox_tax_category_a = order.getSpecificTax(21);
        order.blackbox_tax_category_b = order.getSpecificTax(12);
        order.blackbox_tax_category_c = order.getSpecificTax(6);
        order.blackbox_tax_category_d = order.getSpecificTax(0);
        return {
            date: luxon.DateTime.now().toFormat("yyyyMMdd"),
            ticket_time: luxon.DateTime.now().toFormat("HHmmss"),
            insz_or_bis_number: this.config.module_pos_hr
                ? this.get_cashier().insz_or_bis_number
                : this.user.insz_or_bis_number,
            ticket_number: order.sequence_number.toString(),
            type: order.receipt_type
                ? order.receipt_type
                : order.get_total_with_tax() >= 0
                ? "NS"
                : "NR",
            receipt_total: Math.abs(order.get_total_with_tax())
                .toFixed(2)
                .toString()
                .replace(".", ""),
            vat1: order.blackbox_tax_category_a
                ? Math.abs(order.blackbox_tax_category_a).toFixed(2).replace(".", "")
                : "",
            vat2: order.blackbox_tax_category_b
                ? Math.abs(order.blackbox_tax_category_b).toFixed(2).replace(".", "")
                : "",
            vat3: order.blackbox_tax_category_c
                ? Math.abs(order.blackbox_tax_category_c).toFixed(2).replace(".", "")
                : "",
            vat4: order.blackbox_tax_category_d
                ? Math.abs(order.blackbox_tax_category_d).toFixed(2).replace(".", "")
                : "",
            plu: order.getPlu(),
            clock: order.clock ? order.clock : false,
        };
    },
    async pushDataToBlackbox(data) {
        const fdm = this.hardwareProxy.deviceControllers.fiscal_data_module;

        const prom = new Promise((resolve, reject) => {
            fdm.addListener((data) =>
                data.status.status === "connected" ? resolve(data) : reject(data)
            );
        });

        fdm.action({
            action: "registerReceipt",
            high_level_message: data,
        });

        return prom;
    },
    setDataForPushOrderFromBlackbox(order, data) {
        order.receipt_type = order.receipt_type
            ? order.receipt_type
            : order.get_total_with_tax() >= 0
            ? "NS"
            : "NR";
        order.blackbox_signature = data.value.signature;
        order.blackbox_unit_id = data.value.vsc;
        order.blackbox_plu_hash = order.getPlu();
        order.blackbox_vsc_identification_number = data.value.vsc;
        order.blackbox_unique_fdm_production_number = data.value.fdm_number;
        order.blackbox_ticket_counter = data.value.ticket_counter;
        order.blackbox_total_ticket_counter = data.value.total_ticket_counter;
        order.blackbox_ticket_counters =
            order.receipt_type +
            " " +
            data.value.ticket_counter +
            "/" +
            data.value.total_ticket_counter;
        order.blackbox_time = data.value.time.replace(/(\d{2})(\d{2})(\d{2})/g, "$1:$2:$3");
        order.blackbox_date = data.value.date.replace(/(\d{4})(\d{2})(\d{2})/g, "$3-$2-$1");
    },
    cashierHasPriceControlRights() {
        if (this.useBlackBoxBe()) {
            return false;
        } else {
            return super.cashierHasPriceControlRights();
        }
    },
    getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(...arguments);
        result.useBlackBoxBe = this.useBlackBoxBe();
        result.posIdentifier = this.config.name;
        if (order && this.useBlackBoxBe()) {
            result.receipt_type = order.receipt_type;
            result.blackboxDate = order.blackbox_date;
        }
        return result;
    },
});
