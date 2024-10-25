/* global Sha1 */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    doNotAllowRefundAndSales() {
        return this.useBlackBoxBe() || super.doNotAllowRefundAndSales();
    },
    useBlackBoxBe() {
        return this.config.iface_fiscal_data_module;
    },
    checkIfUserClocked() {
        const cashierId = this.user.id;
        if (this.config.module_pos_hr) {
            return this.session.employees_clocked_ids.find((elem) => elem === cashierId);
        }
        return this.session.users_clocked_ids.find((elem) => elem === cashierId);
    },
    getSpecificTax(amount) {
        const tax = this.get_tax_details().find((tax) => tax.tax.amount === amount);
        return tax ? tax.amount : false;
    },
    wait_for_push_order() {
        const result = super.wait_for_push_order();
        return Boolean(this.useBlackBoxBe() || result);
    },
    getPlu() {
        let order_str = "";
        this.get_orderlines().forEach((line) => (order_str += line.generatePluLine()));
        const sha1 = Sha1.hash(order_str);
        return sha1.slice(sha1.length - 8);
    },
    export_for_printing(baseUrl, headerData) {
        const result = super.export_for_printing(...arguments);
        result.useBlackboxBe = Boolean(this.useBlackBoxBe());
        if (this.useBlackBoxBe()) {
            const order = this;
            result.blackboxBeData = {
                pluHash: order.blackbox_plu_hash,
                receipt_type: order.receipt_type,
                terminalId: this.config.id,
                blackboxDate: order.blackbox_date,
                blackboxTime: order.blackbox_time,

                blackboxSignature: order.blackbox_signature,
                versionId: this.config.server_version.server_version,

                vscIdentificationNumber: order.blackbox_vsc_identification_number,
                blackboxFdmNumber: order.blackbox_unique_fdm_production_number,
                blackbox_ticket_counter: order.blackbox_ticket_counter,
                blackbox_total_ticket_counter: order.blackbox_total_ticket_counter,
                ticketCounter: order.blackbox_ticket_counters,
                fdmIdentifier: order.config.certified_blackbox_identifier,
            };
        }
        return result;
    },
});
