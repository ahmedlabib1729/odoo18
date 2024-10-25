# Part of Odoo. See LICENSE file for full copyright and licensing details.


def _get_subscription_data(
    env, product_or_template, pricelist, date=None, currency=None, subscription_plan_id=None,
):
    """ Return data about the provided product's subscription.

    :param Environment env: The environment to use.
    :param product.product|product.template product_or_template: The product for which to get data.
    :param product.pricelist pricelist: The pricelist to use.
    :param datetime|None date: The date to use to compute prices.
    :param res.currency|None currency: The currency of the transaction.
    :param int|None subscription_plan_id: The subscription plan of the product, as a
        `sale.subscription.plan` id.
    :rtype: dict
    :return: A dict with the following structure:
        {
            'price': float,
            'price_info': str,
        }
    """
    subscription_plan = env['sale.subscription.plan'].browse(subscription_plan_id)
    pricing = env['sale.subscription.pricing'].sudo()._get_first_suitable_recurring_pricing(
        product_or_template, plan=subscription_plan, pricelist=pricelist
    )
    if pricing:
        return {
            'price': pricing.currency_id._convert(
                from_amount=pricing.price,
                to_currency=currency,
                company=env.company,
                date=date,
            ),
            'price_info': pricing.plan_id.billing_period_display_sentence,
        }
    return {}
