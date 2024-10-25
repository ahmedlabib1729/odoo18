# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.http import request

from odoo.addons.sale.controllers.combo_configurator import SaleComboConfiguratorController
from odoo.addons.sale_subscription.controllers.utils import _get_subscription_data


class SaleSubscriptionComboConfiguratorController(SaleComboConfiguratorController):

    def _get_combo_product_data(
        self,
        product_template,
        quantity,
        date,
        currency,
        pricelist,
        subscription_plan_id=None,
        **kwargs,
    ):
        """ Override of `sale` to append subscription data.

        :param product.template product_template: The product for which to get data.
        :param int quantity: The quantity of the product.
        :param str date: The date to use to compute prices.
        :param res.currency currency: The currency to use to compute prices.
        :param product.pricelist pricelist: The pricelist to use to compute prices.
        :param int|None subscription_plan_id: The subscription plan of the product, as a
            `sale.subscription.plan` id.
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
            subscription_plan_id=subscription_plan_id,
            **kwargs,
        )

        if product_template.recurring_invoice:
            product_data.update(_get_subscription_data(
                request.env,
                product_template,
                pricelist,
                datetime.fromisoformat(date),
                currency,
                subscription_plan_id,
            ))
        return product_data

    def _get_combo_product_price(
        self,
        product_template,
        quantity,
        date,
        currency,
        pricelist,
        subscription_plan_id=None,
        **kwargs
    ):
        """ Override of `sale` to compute the subscription price.

        :param product.template product_template: The product for which to get data.
        :param int quantity: The quantity of the product.
        :param str date: The date to use to compute prices.
        :param res.currency currency: The currency to use to compute prices.
        :param product.pricelist pricelist: The pricelist to use to compute prices.
        :param dict kwargs: Locally unused data passed to `_get_product_price`.
        :rtype: dict
        :return: The specified product's price.
        """
        price = super()._get_combo_product_price(
            product_template,
            quantity,
            date,
            currency,
            pricelist,
            subscription_plan_id=subscription_plan_id,
            **kwargs,
        )
        if product_template.recurring_invoice:
            price = _get_subscription_data(
                request.env,
                product_template,
                pricelist,
                datetime.fromisoformat(date),
                currency,
                subscription_plan_id,
            ).get('price', price)
        return price
