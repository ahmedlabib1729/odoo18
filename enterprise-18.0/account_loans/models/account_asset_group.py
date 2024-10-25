from odoo import fields, models, api


class AccountAssetGroup(models.Model):
    _inherit = 'account.asset.group'

    linked_loan_ids = fields.One2many('account.loan', 'asset_group_id', string='Related Loans')
    count_linked_loans = fields.Integer(compute="_compute_count_linked_loans")

    @api.depends('linked_loan_ids')
    def _compute_count_linked_loans(self):
        for asset_group, count_linked_loans in self.env['account.loan']._read_group(
            [('asset_group_id', 'in', self.ids)],
            ['asset_group_id'], ['__count']
        ):
            asset_group.count_linked_loans = count_linked_loans

    def action_open_linked_loans(self):
        self.ensure_one()
        return {
            'name': self.name,
            'view_mode': 'list,form',
            'res_model': 'account.loan',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.linked_loan_ids.ids)],
        }
