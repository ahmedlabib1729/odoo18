# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_amount


class product_template(models.Model):
    _inherit = "product.template"

    recurring_invoice = fields.Boolean(
        'Subscription Product',
        help='If set, confirming a sale order with this product will create a subscription')

    product_subscription_pricing_ids = fields.One2many(
        'sale.subscription.pricing', 'product_template_id', string="Custom Subscription Pricings",
        auto_join=True, copy=False, groups='sales_team.group_sale_salesman'
    )
    display_subscription_pricing = fields.Char('Display Price', compute='_compute_display_subscription_pricing')

    @api.model
    def _get_incompatible_types(self):
        return ['recurring_invoice'] + super()._get_incompatible_types()

    @api.onchange('recurring_invoice')
    def _onchange_recurring_invoice(self):
        """
        Raise a warning if the user has checked 'Subscription Product'
        while the product has already been sold.
        In this case, the 'Subscription Product' field is automatically
        unchecked.
        """
        confirmed_lines = self.env['sale.order.line'].search([
            ('product_template_id', 'in', self.ids),
            ('state', '=', 'sale')])
        if confirmed_lines:
            self.recurring_invoice = not self.recurring_invoice
            return {'warning': {
                'title': _("Warning"),
                'message': _(
                    "You can not change the recurring property of this product because it has been sold already.")
            }}

    @api.depends('product_subscription_pricing_ids')
    def _compute_display_subscription_pricing(self):
        for record in self:
            if record.product_subscription_pricing_ids:
                display_pricing = record.product_subscription_pricing_ids[0]
                formatted_price = format_amount(self.env, display_pricing.price, display_pricing.currency_id)
                record.display_subscription_pricing = _(
                    '%(price)s %(billing_period_display_sentence)s',
                    price=formatted_price,
                    billing_period_display_sentence=display_pricing.plan_id.billing_period_display_sentence
                )
            else:
                record.display_subscription_pricing = None

    @api.constrains('type', 'combo_ids', 'recurring_invoice')
    def _check_subscription_combo_ids(self):
        for template in self:
            if (
                template.type == 'combo'
                and template.recurring_invoice
                and any(
                    not product.recurring_invoice
                    for product in template.combo_ids.combo_item_ids.product_id
                )
            ):
                raise ValidationError(
                    _("A subscription combo product can only contain subscription products.")
                )

    def copy(self, default=None):
        copied_tmpls = self.env['product.template']
        for record in self:
            copied_tmpl = super(product_template, record).copy(default)
            copied_tmpls += copied_tmpl
            for pricing in record.product_subscription_pricing_ids:
                copied_variant_ids = []
                for product in pricing.product_variant_ids:
                    pav_ids = product\
                        .product_template_variant_value_ids\
                        .product_attribute_value_id\
                        .ids
                    copied_variant_ids.extend(
                        copied_tmpl.product_variant_ids.filtered(
                            lambda p: p
                                .product_template_variant_value_ids
                                .product_attribute_value_id
                                .ids == pav_ids
                        ).ids
                    )
                pricing.copy({
                    'product_template_id': copied_tmpl.id,
                    'product_variant_ids': copied_variant_ids,
                })
        return copied_tmpls
