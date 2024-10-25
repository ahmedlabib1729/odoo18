import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Navbar } from "@point_of_sale/app/navbar/navbar";

patch(Navbar.prototype, {
    async showLoginScreen() {
        if (this.pos.useBlackBoxBe() && this.pos.checkIfUserClocked()) {
            this.pos.env.services.dialog.add(AlertDialog, {
                title: _t("Fiscal Data Module Restriction"),
                body: _t("You must clock out in order to change the current employee."),
            });
            return;
        }
        super.showLoginScreen();
    },
});
