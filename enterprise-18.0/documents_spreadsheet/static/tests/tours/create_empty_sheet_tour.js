/** @odoo-module **/

import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("spreadsheet_create_empty_sheet", {
    test: true,
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="documents.menu_root"]',
            content: "Open document app",
            run: "click",
        },
        {
            trigger: '.o_kanban_record:contains("Test folder")',
            content: "Open the test folder",
            run: "dblclick",
        },
        {
            trigger: ".o_cp_buttons:contains('New') .dropdown-toggle",
            content: "Open dropdown",
            run: "click",
        },
        {
            trigger: ".o_documents_kanban_spreadsheet",
            content: "Open template dialog",
            run: "click",
        },
        {
            trigger: ".o-spreadsheet-create",
            content: "Create new spreadsheet",
            run: "click",
        },
        {
            trigger: 'span[title="Fill Color"]',
            content: "Choose a color",
            run: "click",
        },
        {
            trigger: '.o-color-picker-line-item[data-color="#990000"]',
            content: "Choose a color",
            run: "click",
        },
        {
            trigger: ".o-sp-breadcrumb",
            content: "Go back to Document App",
            run: "click",
        },
        {
            trigger: ".o_document_spreadsheet:first",
            content: "Reopen the sheet",
            run: "click",
        },
        {
            trigger: ".o-sp-breadcrumb",
            content: "Wait for the spreadsheet to be properly unloaded",
            run: "click",
        },
    ],
});
