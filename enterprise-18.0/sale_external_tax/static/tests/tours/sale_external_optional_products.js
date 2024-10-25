/** @odoo-module **/

import { registry } from "@web/core/registry";

// This tour relies on data created on the Python test.
registry.category("web_tour.tours").add('sale_external_optional_products', {
    test: true,
    url: '/my/quotes',
    steps: () => [
    {
        content: "open the test SO",
        trigger: 'a:contains("test")',
        run: "click",
    },
    {
        content: "add the optional product",
        trigger: '.js_add_optional_products',
        run: "click",
    },
    {
        trigger: 'li a:contains("Communication history")', // Element on the left
    },
    {
        content: "increase the quantity of the optional product by 1",
        trigger: '.js_update_line_json:eq(1)',
        run: "click",
    },
    {
        trigger: 'li a:contains("Communication history")',
    },
    {
        content: "wait for the quantity to be updated",
        trigger: 'input.js_quantity:value(2.0)',
    },
    {
        content: "delete the optional line",
        trigger: '.js_update_line_json:eq(2)',
        run: "click",
    },
    {
        content: "wait for line to be deleted and show up again in optional products",
        trigger: '.js_add_optional_products',
    },
]});
