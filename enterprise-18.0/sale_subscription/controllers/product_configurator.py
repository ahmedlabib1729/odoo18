# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request

from odoo.addons.sale.controllers.product_configurator import SaleProductConfiguratorController
from odoo.addons.sale_subscription.controllers.utils import _get_subscription_data


class SaleSubscriptionProductConfiguratorController(SaleProductConfiguratorController):

    def _get_basic_product_information(
        self,
        product_or_template,
        pricelist,
        combination,
        currency=None,
        date=None,
        subscription_plan_id=None,
        **kwargs,
    ):
        """ Override of `sale` to append subscription data.

        :param product.product|product.template product_or_template: The product for which to seek
            information.
        :param product.pricelist pricelist: The pricelist to use.
        :param product.template.attribute.value combination: The combination of the product.
        :param res.currency|None currency: The currency of the transaction.
        :param datetime|None date: The date of the `sale.order`, to compute the price at the right
            rate.
        :param int|None subscription_plan_id: The subscription plan of the product, as a
            `sale.subscription.plan` id.
        :param dict kwargs: Locally unused data passed to `super`.
        :rtype: dict
        :return: A dict containing data about the specified product.
        """
        basic_product_information = super()._get_basic_product_information(
            product_or_template,
            pricelist,
            combination,
            currency=currency,
            date=date,
            subscription_plan_id=subscription_plan_id,
            **kwargs,
        )

        if product_or_template.recurring_invoice:
            basic_product_information.update(_get_subscription_data(
                request.env,
                product_or_template,
                pricelist,
                date,
                currency,
                subscription_plan_id,
            ))
        return basic_product_information
