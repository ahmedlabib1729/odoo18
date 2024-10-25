/** @odoo-module **/

import { Asserts } from "./asserts";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('account_reports_sections', {
    test: true,
    url: "/odoo/action-account_reports.action_account_report_gt",
    steps: () => [
        {
            content: "Open variant selector",
            trigger: "#filter_variant button",
            run: 'click',
        },
        {
            content: "Select the test variant using sections",
            trigger: ".dropdown-item:contains('Test Sections')",
            run: 'click',
        },
        {
            content: "Check the lines of section 1 are displayed",
            trigger: ".line_name:contains('Section 1 line')",
        },
        {
            content: "Check the columns of section 1 are displayed",
            trigger: "#table_header th:last():contains('Column 1')",
        },
        {
            content: "Check the export buttons belong to the composite report",
            trigger: ".btn:contains('composite_report_custom_button')",
        },
        {
            content: "Check the filters displayed belong to section 1 (journals filter is not enabled on section 2, nor the composite report)",
            trigger: "#filter_journal",
        },
        {
            content: "Check the date chosen by default",
            trigger: "#filter_date",
            run: (actionHelper) => {
                const currentYear = new Date().getFullYear();

                Asserts.isTrue(actionHelper.anchor.getElementsByTagName('button')[0].innerText.includes(currentYear));
            },
        },
        {
            content: "Switch to section 2",
            trigger: "#section_selector .btn:contains('Section 2')",
            run: 'click',
        },
        {
            content: "Check the lines of section 2 are displayed",
            trigger: ".line_name:contains('Section 2 line')",
        },
        {
            content: "Check the columns of section 2 are displayed",
            trigger: "#table_header th:last():contains('Column 2')",
        },
        {
            content: "Check the export buttons belong to the composite report",
            trigger: ".btn:contains('composite_report_custom_button')",
        },
        {
            content: "Check the filters displayed belong to section 2 (comparison filter is not enabled on section 1, nor the composite report)",
            trigger: "#filter_comparison",
        },
        {
            content: "Open date switcher",
            trigger: "#filter_date button",
            run: 'click',
        },
        {
            content: "Select another date in the future",
            trigger: ".dropdown-menu span.dropdown-item:nth-child(3) .btn_next_date",
            run: 'click'
        },
        {
            content: "Apply filter by closing the dropdown for the future date",
            trigger: "#filter_date .btn:first()",
            run: "click",
        },
        {
            content: "Check that the date has changed",
            trigger: `#filter_date button:not(:contains(${ new Date().getFullYear() }))`,
            run: (actionHelper) => {
                const currentYear = new Date().getFullYear();
                const nextYear = currentYear + 1;

                Asserts.isTrue(actionHelper.anchor.innerText.includes(nextYear));
            },
        },
        {
            content: "Open date switcher",
            trigger: "#filter_date button",
            run: 'click',
        },
        {
            content: "Select another date first time",
            trigger: ".dropdown-menu span.dropdown-item:nth-child(3) .btn_previous_date",
            run: 'click'
        },
        {
            trigger: `.dropdown-menu span.dropdown-item:nth-child(3) time:contains(${new Date().getFullYear()})`,
        },
        {
            content: "Select another date second time",
            trigger: ".dropdown-menu span.dropdown-item:nth-child(3) .btn_previous_date",
            run: 'click'
        },
        {
            trigger: `.dropdown-menu span.dropdown-item:nth-child(3) time:contains(${
                new Date().getFullYear() - 1
            })`,
        },
        {
            content: "Apply filter by closing the dropdown",
            trigger: "#filter_date .btn:first()",
            run: "click",
        },
        {
            content: "Check that the date has changed",
            trigger: `#filter_date button:contains(${ new Date().getFullYear() - 1 })`,
        },
        {
            content: "Switch back to section 1",
            trigger: "#section_selector .btn:contains('Section 1')",
            run: 'click',
        },
    ]
});
