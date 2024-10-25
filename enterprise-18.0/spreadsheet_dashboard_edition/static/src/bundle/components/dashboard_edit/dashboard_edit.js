import { Component, onWillStart } from "@odoo/owl";
import { user } from "@web/core/user";
import { dashboardActionRegistry } from "@spreadsheet_dashboard/bundle/dashboard_action/dashboard_action";

export class DashboardEdit extends Component {
    static template = "spreadsheet_dashboard_edition.DashboardEdit";
    static props = {
        onClick: Function,
    };
    setup() {
        this.isDashboardAdmin = false;
        onWillStart(async () => {
            if (this.env.debug) {
                this.isDashboardAdmin = await user.hasGroup(
                    "spreadsheet_dashboard.group_dashboard_manager"
                );
            }
        });
    }
}

dashboardActionRegistry.add("dashboard_edit", DashboardEdit);
