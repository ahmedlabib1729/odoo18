# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    document_spreadsheet_folder_id = fields.Many2one(
        'documents.document', check_company=True,
        default=lambda self:
            self.env.ref('documents_spreadsheet.document_spreadsheet_folder',
            raise_if_not_found=False),
        domain=[('type', '=', 'folder'), ('shortcut_document_id', '=', False)],
    )
