/** @odoo-module **/

import { registry } from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("test_checkout_id_nit", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({ productName: "Test Product" }),
        tourUtils.goToCart({ quantity: 1 }),
        {
            content: "Go to checkout",
            trigger: "a[name='website_sale_main_button']",
            run: 'click',
        },
        {
            content: "Fill Billing Form",
            trigger: 'form.checkout_autoformat',
            run: function() {
                $('select[name="country_id"]').val($('#o_country_id option[code="CO"]').val()).change();
                $('input[name="name"]').val('abc');
                $('input[name="phone"]').val('99999999');
                $('input[name="email"]').val('abc@odoo.com');
                $('input[name="street"]').val('SO1 Billing Street, 33');
                $('input[name="zip"]').val('10000');
                $('input[name="company_name"]').val('Test Name');
                const nit_id = $('select[name="l10n_latam_identification_type_id"] option').filter(() => $(this).text().trim() === 'NIT');
                $('select[name="l10n_latam_identification_type_id"]').val(nit_id.val()).change();
                $('input[name="vat"]').val('213123432-1');
                // When ID is NIT, fill out the Obligation Types field
                const obligation_id = $("select[name='l10n_co_edi_obligation_type_ids'] option").filter(() => $(this).text().trim() === 'R-99-PN');
                $("select[name='l10n_co_edi_obligation_type_ids']").val(obligation_id.val());
            },
        },
        {
            content: "Fill State and City",
            trigger: "select[name='city_id']",
            run: function() {
                $('select[name="state_id"]').val($('select[name="state_id"] option:eq(1)').val());
                $('select[name="city_id"]').val($('select[name="city_id"] option:eq(1)').val());
            },
        },
        {
            content: "Continue Checkout",
            trigger: '.btn-primary:contains("Continue checkout")',
            run: 'click',
        },
    ],
});

registry.category("web_tour.tours").add("test_checkout_other_id", {
    test: true,
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({ productName: "Test Product" }),
        tourUtils.goToCart({ quantity: 1 }),
        {
            content: "Go to checkout",
            trigger: "a[name='website_sale_main_button']",
            run: 'click',
        },
        {
            content: "Fill Billing Form",
            trigger: 'form.checkout_autoformat',
            run: function() {
                $('select[name="country_id"]').val($('#o_country_id option[code="CO"]').val()).change();
                $('input[name="name"]').val('abc');
                $('input[name="phone"]').val('99999999');
                $('input[name="email"]').val('abc@odoo.com');
                $('input[name="street"]').val('SO1 Billing Street, 33');
                $('input[name="zip"]').val('10000');
                const civil_id = $('select[name="l10n_latam_identification_type_id"] option').filter(() =>  $(this).text().trim() === 'Registro Civil');
                $('select[name="l10n_latam_identification_type_id"]').val(civil_id.val()).change();
                $('input[name="vat"]').val('213123432-1');
            },
        },
        {
            content: "Fill the city and state",
            trigger: "select[name='city_id']",
            run: function() {
                $('select[name="state_id"]').val($('select[name="state_id"] option:eq(1)').val());
                $('select[name="city_id"]').val($('select[name="city_id"] option:eq(1)').val());
            },
        },
        {
            content: "Validate address",
            trigger: '.btn-primary:contains("Continue checkout")',
            run: 'click',
        },
    ],
});
