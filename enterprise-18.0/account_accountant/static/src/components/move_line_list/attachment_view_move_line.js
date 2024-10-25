import { AttachmentView } from "@mail/core/common/attachment_view";
import { onMounted } from "@odoo/owl";
import { useBus } from "@web/core/utils/hooks";

export class AttachmentViewMoveLine extends AttachmentView {
    static props = [...AttachmentView.props, "openInPopout"];
    static components = { AttachmentView };

    setup() {
        super.setup();
        if (this.props.openInPopout) {
            onMounted(this.popoutAttachment);
        }
        // In the mail_popout_service.js the function pollClosedWindow will trigger a resize event on the main window
        // when the external window is closed. It allow us to know when to hide the preview for small screens.
        useBus(this.uiService.bus, "resize", this.updateViewPopup);
    }

    popoutAttachment() {
        /**
         * This function will get the div of the PDF in the view and then call the popout service to make the external
         * view
         */
        const view = this.__owl__.bdom.parentEl.querySelector("o-mail-attachment");
        this.mailPopoutService.popout(view).focus();
    }

    updateViewPopup() {
        /**
         * This function will get called when the external window is closed, to avoid the preview attachment to be
         * displayed in the view at that time, we add the "d-none" class to hide it. And then, we reset the popout variable
         * to false, so that the external value is not launched when clicking on the line again.
         */
        const view = this.__owl__.bdom.parentEl;
        view.classList.add("d-none");
        this.env.setPopout(false);
    }
}
