# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    account_represented_company_ids = fields.One2many('res.company', 'account_representative_id')

    def open_partner_ledger(self):
        action = self.env["ir.actions.actions"]._for_xml_id("account_reports.action_account_report_partner_ledger")
        action['params'] = {
            'options': {'partner_ids': self.ids, 'unfold_all': len(self.ids) == 1},
            'ignore_session': True,
        }
        return action

    def open_partner(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.id,
            'views': [[False, 'form']],
            'view_mode': 'form',
            'target': 'current',
        }

    @api.depends_context('show_more_partner_info')
    def _compute_display_name(self):
        if not self.env.context.get('show_more_partner_info'):
            return super()._compute_display_name()
        for partner in self:
            res = ""
            if partner.vat:
                res += f" {partner.vat},"
            if partner.country_id:
                res += f" {partner.country_id.code},"
            partner.display_name = f"{partner.name} - " + res
