/** @odoo-module **/

import { EventBus } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

import mobile from "@web_mobile/js/services/core";
import { shortcutItem, switchAccountItem } from "./user_menu_items";

const serviceRegistry = registry.category("services");
const userMenuRegistry = registry.category("user_menuitems");

export const mobileService = {
    timeBetweenReadsInMs: session.time_between_reads_in_ms || 100,
    idInterval: null,
    start() {
        this.bus = new EventBus();

        if (mobile.methods.addHomeShortcut) {
            userMenuRegistry.add("web_mobile.shortcut", shortcutItem);
        }

        if (mobile.methods.switchAccount) {
            // remove "Log Out" and "My Odoo.com Account"
            userMenuRegistry.remove('log_out');
            userMenuRegistry.remove('odoo_account');

            userMenuRegistry.add("web_mobile.switch", switchAccountItem);
        }

        this.enableReader();

        return {
            bus: this.bus,
            enableReader: this.enableReader,
            stopReader: this.stopReader,
        };
    },

    enableReader() {
        if (mobile.methods.enableReader && mobile.methods.getReaderData) {
            mobile.methods.enableReader();
            if (!this.idInterval) {
                this.idInterval = setInterval(async () => {
                    try {
                        const value = await mobile.methods.getReaderData();
                        if (value.success) {
                            const data = value.data;
                            if (data.length > 0) {
                                this.bus.trigger("mobile_reader_scanned", {data});
                            }
                        }
                    } catch (e) {
                        console.error(e);
                    }
                }, this.timeBetweenReadsInMs);
            }
        }
    },

    stopReader() {
        if (this.idInterval) {
            clearInterval(this.idInterval);
            this.idInterval = null;
        }
    },
};
serviceRegistry.add("mobile", mobileService);
