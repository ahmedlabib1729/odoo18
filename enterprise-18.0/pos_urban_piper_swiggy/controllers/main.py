from odoo.addons.pos_urban_piper.controllers.main import PosUrbanPiperController
from odoo.http import request


class PosSwiggyController(PosUrbanPiperController):

    def _get_tax_value(self, taxes_data, pos_config):
        taxes = super()._get_tax_value(taxes_data, pos_config)
        if request.env.ref('pos_urban_piper_swiggy.pos_delivery_provider_swiggy', False) in pos_config.urbanpiper_delivery_provider_ids:
            tax_lst = []
            for tax_line in taxes_data:
                tax = request.env['account.tax'].sudo().search([
                    ('tax_group_id.name', '=', tax_line.get('title')),
                    ('amount', '=', tax_line.get('rate')),
                ], limit=1)
                if tax:
                    tax_lst.append(tax.id)
            taxes = request.env['account.tax'].sudo().search([('children_tax_ids', 'in', tax_lst)])
        return taxes
