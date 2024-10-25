from odoo import models


class SpreadsheetDummy(models.Model):
    _inherit = ['spreadsheet.test']

    def action_open_spreadsheet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'fake_action',
            'params': {
                'spreadsheet_id': self.id,
            }
        }

    def _creation_msg(self):
        return "test spreadsheet created"

    def _get_spreadsheet_selector(self):
        if not self.env.registry.in_test_mode():
            return None
        return {
            "model": self._name,
            "display_name": "Test spreadsheets",
            "sequence": 100,
        }
