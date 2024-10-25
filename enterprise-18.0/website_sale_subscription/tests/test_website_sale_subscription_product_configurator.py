# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestWebsiteSaleSubscriptionProductConfigurator(HttpCase):

    def test_website_sale_subscription_product_configurator(self):
        plan_weekly = self.env['sale.subscription.plan'].create({
            'name': "1 week", 'billing_period_value': 1, 'billing_period_unit': 'week'
        })
        plan_monthly = self.env['sale.subscription.plan'].create({
            'name': "1 month", 'billing_period_value': 1, 'billing_period_unit': 'month'
        })
        optional_product = self.env['product.template'].create({
            'name': "Optional product",
            'website_published': True,
            'recurring_invoice': True,
            'product_subscription_pricing_ids': [
                Command.create({'plan_id': plan_weekly.id, 'price': 6}),
                Command.create({'plan_id': plan_monthly.id, 'price': 16}),
            ],
        })
        self.env['product.template'].create({
            'name': "Main product",
            'website_published': True,
            'recurring_invoice': True,
            'product_subscription_pricing_ids': [
                Command.create({'plan_id': plan_weekly.id, 'price': 5}),
                Command.create({'plan_id': plan_monthly.id, 'price': 15}),
            ],
            'optional_product_ids': [Command.set(optional_product.ids)],
        })
        self.start_tour('/', 'website_sale_subscription_product_configurator', login='admin')
