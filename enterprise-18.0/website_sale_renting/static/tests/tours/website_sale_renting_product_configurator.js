/** @odoo-module **/

import { registry } from '@web/core/registry';
import configuratorTourUtils from '@sale/js/tours/product_configurator_tour_utils';

registry
    .category('web_tour.tours')
    .add('website_sale_renting_product_configurator', {
        test: true,
        url: '/shop?search=Main product',
        steps: () => [
            {
                content: "Select Main product",
                trigger: '.oe_product_cart a:contains("Main product")',
                run: 'click',
            },
            {
                content: "Click on add to cart",
                trigger: '#add_to_cart',
                run: 'click',
            },
            // Assert that the rental prices and durations are correct.
            configuratorTourUtils.assertProductPrice("Main product", '5.00'),
            configuratorTourUtils.assertProductPriceInfo("Main product", "3 Hours"),
            configuratorTourUtils.assertOptionalProductPrice("Optional product", '6.00'),
            configuratorTourUtils.assertOptionalProductPriceInfo("Optional product", "3 Hours"),
            {
                content: "Proceed to checkout",
                trigger: 'button:contains(Proceed to Checkout)',
                run: 'click',
            },
            {
                content: "Verify the rental price and duration in the cart",
                trigger: 'div.o_cart_product div:contains(5.00 / 3 Hours)',
            },
        ],
   });
