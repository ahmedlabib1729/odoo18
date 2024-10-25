from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_co_dian_operation_mode_ids = fields.One2many(
        string="DIAN Operation Modes",
        comodel_name="l10n_co_dian.operation_mode",
        inverse_name="company_id",
    )
    l10n_co_dian_certificate_ids = fields.One2many(comodel_name='certificate.certificate', inverse_name='company_id')
    l10n_co_dian_test_environment = fields.Boolean(string="Test environment", default=True)
    l10n_co_dian_certification_process = fields.Boolean()
    l10n_co_dian_provider = fields.Selection(
        selection=[
            ('dian', "DIAN: Free service"),
            ('carvajal', "Carvajal")
        ],
        default=lambda self: self._default_l10n_co_dian_provider(),
    )

    def write(self, vals):
        if vals.get('l10n_co_dian_test_environment') is False:
            # The test environment should be used during the certification process
            vals['l10n_co_dian_certification_process'] = False
        return super().write(vals)

    def _default_l10n_co_dian_provider(self):
        carvajal_id = self.env.ref('l10n_co_edi.edi_carvajal').id
        if self.env['account.edi.document'].with_company(self.env.company).search([
            ('edi_format_id', '=', carvajal_id)
        ], limit=1):
            return 'carvajal'
        else:
            return 'dian'
