# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route

from odoo.addons.sale.controllers.combo_configurator import SaleComboConfiguratorController
from odoo.addons.sale_renting.controllers.utils import _convert_rental_dates, _get_renting_data


class SaleRentingComboConfiguratorController(SaleComboConfiguratorController):

    @route()
    def sale_combo_configurator_get_data(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_combo_configurator_get_data(*args, **kwargs)

    @route()
    def sale_combo_configurator_get_price(self, *args, **kwargs):
        _convert_rental_dates(kwargs)
        return super().sale_combo_configurator_get_price(*args, **kwargs)

    def _get_combo_product_data(
        self,
        product_template,
        quantity,
        date,
        currency,
        pricelist,
        start_date=None,
        end_date=None,
        **kwargs,
    ):
        """ Override of `sale` to append rental data.

        :param product.template product_template: The product for which to get data.
        :param int quantity: The quantity of the product.
        :param str date: The date to use to compute prices.
        :param res.currency currency: The currency to use to compute prices.
        :param product.pricelist pricelist: The pricelist to use to compute prices.
        :param datetime|None start_date: The rental start date, to compute the rental duration.
        :param datetime|None end_date: The rental end date, to compute the rental duration.
        :param dict kwargs: Locally unused data passed to `super`.
        :rtype: dict
        :return: A dict containing data about the specified product.
        """
        product_data = super()._get_combo_product_data(
            product_template,
            quantity,
            date,
            currency,
            pricelist,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

        if product_template.rent_ok:
            product_data.update(_get_renting_data(
                request.env,
                product_template,
                pricelist,
                currency,
                start_date,
                end_date,
            ))
        return product_data
