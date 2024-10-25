import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
patch(ClosePosPopup.prototype, {
    async confirm() {
        if (this.pos.useBlackBoxBe()) {
            const status = await this.getUserSessionStatus(this.pos.session.user_id[0]);
            if (status) {
                this.pos.env.services.dialog.add(AlertDialog, {
                    title: _t("POS error"),
                    body: _t("You need to clock out before closing the POS."),
                });
                return;
            }
        }
        return super.confirm();
    },
    async getUserSessionStatus(session, user) {
        return await this.pos.data.call("pos.session", "get_user_session_work_status", [
            [this.pos.session.id],
            user,
        ]);
    },
});
