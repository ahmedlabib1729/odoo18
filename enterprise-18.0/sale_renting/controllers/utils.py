# Part of Odoo. See LICENSE file for full copyright and licensing details.

from math import ceil

from odoo import fields


def _convert_rental_dates(kwargs):
    kwargs.update({
        'start_date': fields.Datetime.to_datetime(kwargs.get('start_date')),
        'end_date': fields.Datetime.to_datetime(kwargs.get('end_date')),
    })


def _get_renting_data(
    env, product_or_template, pricelist, currency=None, start_date=None, end_date=None,
):
    """ Return data about the provided product's rental.

    :param Environment env: The environment to use.
    :param product.product|product.template product_or_template: The product for which to get data.
    :param product.pricelist pricelist: The pricelist to use.
    :param res.currency|None currency: The currency of the transaction.
    :param datetime|None start_date: The rental start date, to compute the rental duration.
    :param datetime|None end_date: The rental end date, to compute the rental duration.
    :rtype: dict
    :return: A dict with the following structure:
        {
            'price_info': str,
        }
    """
    if start_date and end_date:
        pricing = product_or_template._get_best_pricing_rule(
            start_date=start_date,
            end_date=end_date,
            pricelist=pricelist,
            currency=currency,
        )
        if pricing:
            rental_duration = env['product.pricing']._compute_duration_vals(
                start_date, end_date
            )[pricing.recurrence_id.unit]
            return {
                # Some locales might swap the duration and the unit, so we need to use the
                # translation function.
                'price_info': env._(
                    "%(duration)s %(unit)s",
                    duration=ceil(rental_duration),
                    unit=pricing.recurrence_id._get_unit_label(rental_duration),
                ),
            }
    return {}
