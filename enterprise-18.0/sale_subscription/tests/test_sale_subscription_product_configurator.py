# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestSaleSubscriptionProductConfigurator(HttpCase):

    def test_sale_subscription_product_configurator(self):
        self.env['res.partner'].create({'name': "Customer"})
        plan_weekly = self.env['sale.subscription.plan'].create({
            'name': "1 week", 'billing_period_value': 1, 'billing_period_unit': 'week'
        })
        plan_monthly = self.env['sale.subscription.plan'].create({
            'name': "1 month", 'billing_period_value': 1, 'billing_period_unit': 'month'
        })
        optional_product = self.env['product.template'].create({
            'name': "Optional product",
            'recurring_invoice': True,
            'product_subscription_pricing_ids': [
                Command.create({'plan_id': plan_weekly.id, 'price': 6}),
                Command.create({'plan_id': plan_monthly.id, 'price': 16}),
            ],
        })
        self.env['product.template'].create({
            'name': "Main product",
            'recurring_invoice': True,
            'product_subscription_pricing_ids': [
                Command.create({'plan_id': plan_weekly.id, 'price': 5}),
                Command.create({'plan_id': plan_monthly.id, 'price': 15}),
            ],
            'optional_product_ids': [Command.set(optional_product.ids)],
        })
        self.start_tour('/', 'sale_subscription_product_configurator', login='admin')
