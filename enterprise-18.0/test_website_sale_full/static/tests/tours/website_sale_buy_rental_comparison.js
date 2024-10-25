/** @odoo-module **/

import { registry } from "@web/core/registry";
import * as tourUtils from '@website_sale/js/tours/tour_utils';

registry.category("web_tour.tours").add('shop_buy_rental_product_comparison', {
    test: true,
    url: '/shop?search=Computer',
    steps: () => [
        {
            content: "click on add to comparison",
            trigger: '.o_add_compare',
            run: "click",
        },
        {
            content: "Search Warranty write text",
            trigger: 'form input[name="search"]',
            run: "edit Warranty",
        },
        {
            content: "Search Warranty click",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
            run: "click",
        },
        {
            content: "add first product 'Warranty' in a comparison list",
            trigger: '.oe_product_cart:contains("Warranty") .o_add_compare',
            run: "click",
        },
        {
            trigger: ".comparator-popover",
        },
        {
            content: "check popover is now open and compare button contains two products",
            trigger: '.o_product_circle:contains(2)',
        },
        {
            content: "click on compare button",
            trigger: '.o_comparelist_button a',
            run: "click",
        },
        {
            content: "click on add to cart",
            trigger: '.product_summary:contains("Computer") .a-submit:contains("Add to Cart")',
            run: "click",
        },
        tourUtils.goToCart({quantity: 1}),
        {
            content: "Verify there is a Computer",
            trigger: '#cart_products div a h6:contains("Computer")',
        },
        {
            content: "Verify there are 1 quantity of Computers",
            trigger: '#cart_products div div.css_quantity input[value="1"]',
        },
        {
            trigger: "#cart_products .oe_currency_value:contains(75.00)",
        },
        {
            content: "go to checkout",
            trigger: 'a[href*="/shop/checkout"]',
            run: "click",
        },
        {
            content: "verify checkout page",
            trigger: 'span div.o_wizard_step_active:contains("Payment")',
        },
    ]
});
