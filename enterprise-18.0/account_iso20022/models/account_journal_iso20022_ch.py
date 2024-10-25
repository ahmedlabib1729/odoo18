from lxml import etree
from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def get_document_namespace(self, payment_method_code):
        if payment_method_code == 'iso20022_ch':
            return 'http://www.six-interbank-clearing.com/de/pain.001.001.03.ch.02.xsd'
        return super().get_document_namespace(payment_method_code)

    def _skip_CdtrAgt(self, partner_bank, payment_method_code):
        # Creditor Agent can be omitted with IBAN and QR-IBAN accounts
        if payment_method_code == 'iso20022_ch' and self._is_qr_iban({'partner_bank_id': partner_bank.id, 'journal_id': self.id}):
            return True
        return super()._skip_CdtrAgt(partner_bank, payment_method_code)

    def _get_SvcLvlText(self, payment_method_code):
        if payment_method_code == 'iso20022_ch':
            return False
        return super()._get_SvcLvlText(payment_method_code)

    def _get_Dbtr(self, payment_method_code):
        Dbtr = super()._get_Dbtr(payment_method_code)
        if payment_method_code == 'iso20022_ch':
            result = list(filter(lambda x: x.tag != 'Id', Dbtr))
            new_dbtr = etree.Element('Dbtr')
            new_dbtr.extend(result)
            return new_dbtr
        return Dbtr
