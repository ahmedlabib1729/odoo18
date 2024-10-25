/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_shop_floor", {
    test: true,
    steps: () => [
    {
        content: 'Select the workcenter the first time we enter in shopfloor',
        trigger: '.form-check:has(input[name="Jungle"])',
        run: "click",
    },
    {
        trigger: '.form-check:has(input[name="Jungle"]:checked)',
    },
    {
        trigger: 'footer.modal-footer button.btn-primary',
        run: "click",
    },
    {
        trigger: '.o_control_panel_actions button:contains("Jungle")',
    },
    {
        content: 'Open the employee panel',
        trigger: 'button[name="employeePanelButton"]',
        run: "click",
    },
    {
        content: 'Add operator button',
        trigger: 'button:contains("Operator")',
        run: "click",
    },
    {
        content: 'Select the Marc Demo employee',
        trigger: '.modal-body .o_mrp_employee_tree_view .o_data_row td:contains("Billy Demo")',
        run: "click",
    },
    {
        trigger: '.o_mrp_employees_panel li.o_admin_user:contains(Billy Demo)',
    },
    {
        content: 'Go to workcenter Savannah from MO card',
        trigger: '.o_mrp_record_line button span:contains("Savannah")',
        run: "click",
    },
    {
        trigger: '.o_control_panel_actions button.active:contains("Savannah")',
    },
    {
        content: 'Start the workorder on header click',
        trigger: '.o_finished_product span:contains("Giraffe")',
        run: "click",
    },
    {
        content: "Register production check",
        trigger: ".modal:not(.o_inactive_modal) .btn.fa-plus",
        run: "click",
    },
    {
        content: "Validate production check",
        trigger: '.modal:not(.o_inactive_modal) button:contains("Validate"):enabled',
        run: "click",
    },
    {
        trigger:
            '.modal:not(.o_inactive_modal):contains(Instructions) button[barcode_trigger="NEXT"]',
        run: "scan OBTNEXT",
    },
    {
        trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Register legs")',
    },
    {
        content: "Component not tracked registration and continue production",
        trigger:
            '.modal:not(.o_inactive_modal):contains(Register legs) button[barcode_trigger="CONT"]',
        run: "click",
    },
    {
        trigger: '.o_field_widget[name="qty_done"] input:value("0.00")',
    },
    {
        content: "Add 2 units",
        trigger: '.o_field_widget[name="qty_done"] input',
        run: "edit 2 && click .modal-body",
    },
    {
        trigger: '.o_field_widget[name="qty_done"] input:value("2.00")',
    },
    {
        content: 'Click on "Validate"',
        trigger: 'button[barcode_trigger="NEXT"]',
        run: "click",
    },
    {
        trigger: '.o_field_widget[name="lot_id"] input:value("NE1")',
    },
    {
        trigger: 'div.o_field_widget[name="lot_id"] input ',
        tooltipPosition: 'bottom',
        run: "edit NE2",
    },
    {
        trigger: `.ui-menu-item > a:contains("NE2")`,
        run: "click",
    },
    {
        trigger: 'button[barcode_trigger="CONT"]',
        run: "click",
    },
    {
        trigger: '.o_field_widget[name="lot_id"] input:value("NE1")',
    },
    {
        trigger: 'button[barcode_trigger="NEXT"]',
        run: "click",
    },
    {
        trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Release")',
    },
    {
        trigger: ".modal:not(.o_inactive_modal) .modal-header .btn-close",
        run: "click",
    },
    {
        content: 'Open instruction',
        trigger: 'button:contains("Instructions")',
        run: "click",
    },
    {
        trigger: '.modal:not(.o_inactive_modal) .modal-title:contains("Release")',
    },
    {
        trigger: '.modal:not(.o_inactive_modal) button[barcode_trigger="NEXT"]',
        run: "click",
    },
    {
        content: "Close first operation",
        trigger: '.card-footer button[barcode_trigger="CLWO"]:contains(Mark as Done)',
        run: "click",
    },
    {
        content: "Navigate to next operation",
        trigger: "button:contains(Next Operation)",
        run: "click",
    },
    {
        trigger: 'div.o_mrp_display_record .card-header .fa-play',
        run: "click",
    },
    {
        content: "Open the WO setting menu again",
        trigger: '.o_mrp_display_record:contains("Release") .card-footer button.fa-gear',
        run: "click",
    },
    {
        content: "Add an operation button",
        trigger: '.modal:not(.o_inactive_modal) button[name="addComponent"]',
        run: "click",
    },
    {
        content: 'Ensure the catalog is opened',
        trigger: '.modal:not(.o_inactive_modal) .o_product_kanban_catalog_view',
    },
    {
        content: 'Add Color',
        trigger: '.modal-body .o_searchview_input',
        run: "edit color && press Enter",
    },
    {
        content: 'Ensure the search is done',
        trigger: '.modal-body div.o_searchview_facet:contains("color")'
    },
    {
        trigger: '.modal-body:not(:has(article.o_kanban_record:not(:contains("Color"))))',
    },
    {
        content: 'Add Color',
        trigger: '.modal article.o_kanban_record:contains("Color") button .fa-shopping-cart',
        run: "click",
    },
    {
        content: 'Ensure the Color product is added',
        trigger: '.modal button .fa-trash',
    },
    {
        content: "Close the catalog",
        trigger: '.modal-header .btn-close',
        run: "click",
    },
    {
        trigger: "body:not(:has(.modal))",
    },
    {
        trigger: 'div.o_mrp_display_record .card-header .fa-pause',
        run: "click",
    },
    {
        trigger: 'div.o_mrp_display_record .card-header .fa-play',
    },
    {
        trigger: ".card-footer button[barcode_trigger=CLWO]:contains(Mark as Done):enabled",
        run: "click",
    },
    {
        trigger: ".card-footer button[barcode_trigger=CLWO]:contains(Undo)",
    },
    {
        trigger: ".card-footer button[barcode_trigger=CLMO]",
        run: "click",
    },
    {
        trigger: ".o_nocontent_help",
    },
    {
        content: "Leave shopfloor",
        trigger: ".o_home_menu .fa-sign-out",
        run: "click",
    },
    {
        trigger: ".o_apps",
    },
    ],
});

registry.category("web_tour.tours").add("test_generate_serials_in_shopfloor", {
    test: true,
    steps: () => [
    {
        content: 'Make sure workcenter is available',
        trigger: '.form-check:has(input[name="Assembly Line"])',
        run: "click",
    },
    {
        trigger: '.form-check:has(input[name="Assembly Line"]:checked)',
    },
    {
        content: 'Confirm workcenter',
        trigger: 'button:contains("Confirm")',
        run: "click",
    },
    {
        content: 'Select workcenter',
        trigger: 'button.btn-light:contains("Assembly Line")',
        run: "click",
    },
    {
        content: 'Open the wizard',
        trigger: '.o_mrp_record_line .text-truncate:contains("Register byprod")',
        run: "click",
    },
    {
        content: 'Open the serials generation wizard',
        trigger: '.o_widget_generate_serials button',
        run: "click",
    },
    {
        content: 'Input a serial',
        trigger: '#next_serial_0',
        run: "edit 00001",
    },
    {
        content: 'Generate the serials',
        trigger: 'button.btn-primary:contains("Generate")',
        run: "click",
    },
    {
        content: 'Save and close the wizard',
        trigger: '.o_form_button_save:contains("Save")',
        run: "click",
    },
    {
        content: 'Set production as done',
        trigger: 'button.btn-primary:contains("Mark as Done")',
        run: "click",
    },
    {
        content: 'Close production',
        trigger: 'button.btn-primary:contains("Close Production")',
    },
    ],
});

registry.category("web_tour.tours").add("test_canceled_wo", {
    test: true,
    steps: () => [
        {
            content: 'Make sure workcenter is available',
            trigger: '.form-check:has(input[name="Assembly Line"])',
            run: "click",
        },
        {
            trigger: '.form-check:has(input[name="Assembly Line"]:checked)',
        },
        {
            content: 'Confirm workcenter',
            trigger: 'button:contains("Confirm")',
            run: "click",
        },
        {
            content: 'Check MO',
            trigger: 'button.btn-light:contains("Assembly Line")',
            run: () => {
                if (document.querySelectorAll("ul button:not(.btn-secondary)").length > 1)
                    console.error("Multiple Workorders");
            },
        },
    ],
});

registry.category("web_tour.tours").add('test_change_qty_produced', {
    test: true, steps: () => [
        {
            content: 'Make sure workcenter is available',
            trigger: '.form-check:has(input[name="WorkCenter"])',
            run: "click",
        },
        {
            content: 'Make sure that Workcenter was checked',
            trigger: '.form-check:has(input[name="WorkCenter"]:checked)',
        },
        {
            content: 'Confirm workcenter',
            trigger: 'button:contains("Confirm")',
            run: "click",
        },
        {
            content: 'Select workcenter',
            trigger: 'button.btn-light:contains("WorkCenter")',
            run: "click",
        },
        {
            content: 'Open the wizard',
            trigger: '.o_mrp_record_line .text-decoration-line-through:contains("Register Production")',
            run: "click",
        },
        {
            content: 'Edit the quantity producing',
            trigger: 'input[inputmode="decimal"]',
            run: "edit 3",
        },
        {
            content: 'Validate',
            trigger: 'button.btn-primary:contains("Validate")',
            run: "click",
        },
        {
            content: 'Waiting modal to close',
            trigger: "body:not(:has(.o_dialog))",
        },
        {
            content: "Mark the WorkOrder as Done",
            trigger: 'button.btn-primary:contains("Mark as Done")',
            run: "click",
        },
        {
            content: "Check if the WO was finished",
            trigger: 'button.btn-primary:contains("Close Production")',
            run: "click",
        },
        {
            content: "Confirm consumption warning",
            trigger: 'button.btn-primary:contains("Confirm")',
            run: "click",
        },
        {
            content: "Dismiss backorder",
            trigger: 'button.btn-secondary:contains("No Backorder")',
            run: "click",
        },
        {
            content: "Check that there are no open work orders",
            trigger: '.o_nocontent_help',
        },
    ]
});
