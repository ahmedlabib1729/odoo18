/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add('sale_subscription_product_variants', {
    test: true,
    steps: () => [
        {
            content: "Trigger first period (Month)",
            trigger: "input[title='Monthly']",
            run: "click",
        },
        {
            content: "Trigger second period (2 Months)",
            trigger: "input[title='2 Months']",
            run: "click",
        },
        {
            content: "Trigger third period (Yearly)",
            trigger: "input[title='Yearly']",
            run: "click",
        },
    ]
});
