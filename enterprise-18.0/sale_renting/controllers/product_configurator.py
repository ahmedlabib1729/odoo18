# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route

from odoo.addons.sale.controllers.product_configurator import SaleProductConfiguratorController
from odoo.addons.sale_renting.controllers.utils import _convert_rental_dates, _get_renting_data


class SaleRentingProductConfiguratorController(SaleProductConfiguratorController):

    @route()
    def sale_product_configurator_get_values(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_get_values(*args, **kwargs)

    @route()
    def sale_product_configurator_update_combination(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_update_combination(*args, **kwargs)

    @route()
    def sale_product_configurator_get_optional_products(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_product_configurator_get_optional_products(*args, **kwargs)

    def _get_basic_product_information(
        self,
        product_or_template,
        pricelist,
        combination,
        currency=None,
        start_date=None,
        end_date=None,
        **kwargs,
    ):
        """ Override of `sale` to append rental data.

        :param product.product|product.template product_or_template: The product for which to seek
            information.
        :param product.pricelist pricelist: The pricelist to use.
        :param product.template.attribute.value combination: The combination of the product.
        :param res.currency|None currency: The currency of the transaction.
        :param datetime|None start_date: The rental start date, to compute the rental duration.
        :param datetime|None end_date: The rental end date, to compute the rental duration.
        :param dict kwargs: Locally unused data passed to `super`.
        :rtype: dict
        :return: A dict containing data about the specified product.
        """
        basic_product_information = super()._get_basic_product_information(
            product_or_template,
            pricelist,
            combination,
            currency=currency,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

        if product_or_template.rent_ok:
            basic_product_information.update(_get_renting_data(
                request.env,
                product_or_template,
                pricelist,
                currency,
                start_date,
                end_date,
            ))
        return basic_product_information
