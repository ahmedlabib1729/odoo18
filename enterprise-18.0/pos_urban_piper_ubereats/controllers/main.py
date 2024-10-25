from odoo.addons.pos_urban_piper.controllers.main import PosUrbanPiperController
from odoo.http import request


class PosUbereatsController(PosUrbanPiperController):

    def _get_tax_value(self, taxes_data, pos_config):
        taxes = super()._get_tax_value(taxes_data, pos_config)
        if request.env.ref('pos_urban_piper_ubereats.pos_delivery_provider_ubereats', False) in pos_config.urbanpiper_delivery_provider_ids:
            for tax_line in taxes_data:
                taxes |= request.env['account.tax'].sudo().search([
                    ('tax_group_id.name', '=', tax_line.get('title')),
                    ('amount', '=', tax_line.get('rate'))
                ], limit=1)
        return taxes
