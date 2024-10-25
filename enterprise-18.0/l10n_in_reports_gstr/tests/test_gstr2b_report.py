# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import tagged
import logging
import json

from odoo.addons.l10n_in_reports_gstr.tests.common import L10nInTestAccountGstReportsCommon

_logger = logging.getLogger(__name__)

@tagged('post_install_l10n', 'post_install', '-at_install')
class TestReports(L10nInTestAccountGstReportsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_b.l10n_in_gst_treatment = "regular"
        cls.partner_foreign.l10n_in_gst_treatment = "overseas"

        cls.fully_matched_bill = cls._init_inv(move_type='in_invoice', ref='INV/001', taxes=cls.comp_igst_18, partner=cls.partner_b)
        cls.fully_matched_bill_refund = cls._create_credit_note(inv=cls.fully_matched_bill, ref='CR/001')

        cls.bill_with_conflict_date = cls._init_inv(move_type='in_invoice', ref='INV/002', taxes=cls.comp_igst_18, partner=cls.partner_b)

        cls.bill_with_conflict_amount = cls._init_inv(move_type='in_invoice', ref='INV/003', taxes=cls.comp_igst_18, partner=cls.partner_b)

        cls.bill_with_conflict_date_amount = cls._init_inv(move_type='in_invoice', ref='INV/004', taxes=cls.comp_igst_18, partner=cls.partner_b)

        cls.bill_with_conflict_type = cls._init_inv(move_type='in_invoice', ref='INV/005', taxes=cls.comp_igst_18, partner=cls.partner_b)
        cls.bill_with_conflict_type_date = cls._create_credit_note(inv=cls.bill_with_conflict_type, ref='CR/002')

        cls.bill_with_conflict_type_amount = cls._init_inv(move_type='in_invoice', ref='INV/006', taxes=cls.comp_igst_18, partner=cls.partner_b)
        cls.bill_with_conflict_type_date_amount = cls._create_credit_note(ref='CR/003', inv=cls.bill_with_conflict_type)

        cls.bill_with_conflict_vat = cls._init_inv(move_type='in_invoice', ref='INV/007', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_date = cls._init_inv(move_type='in_invoice', ref='INV/008', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_amount = cls._init_inv(move_type='in_invoice', ref='INV/009', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_date_amount = cls._init_inv(move_type='in_invoice', ref='INV/010', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_type = cls._init_inv(move_type='in_invoice', ref='INV/011', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_type_date = cls._create_credit_note(ref='CR/004', inv=cls.bill_with_conflict_type)

        cls.bill_with_conflict_vat_type_amount = cls._init_inv(move_type='in_invoice', ref='INV/012', taxes=cls.comp_igst_18, partner=cls.partner_a)

        cls.bill_with_conflict_vat_type_date_amount = cls._create_credit_note(ref='CR/005', inv=cls.bill_with_conflict_type)

        cls.bill_with_conflict_ref = cls._init_inv(move_type='in_invoice', partner=cls.partner_b, taxes=cls.comp_igst_18, line_vals={'price_unit': 2000})

        cls.bill_not_in_gstr2b = cls.bill_with_conflict_ref = cls._init_inv(move_type='in_invoice', ref='INV/404', taxes=cls.comp_igst_18, partner=cls.partner_b)

        cls.overseas_bill = cls.bill_with_conflict_ref = cls._init_inv(move_type='in_invoice', ref='BOE/123', taxes=cls.comp_igst_18, partner=cls.partner_foreign, line_vals={'price_unit': 100000})

        cls.report = cls.gstr_report = cls.env['l10n_in.gst.return.period'].create({
            'company_id': cls.default_company.id,
            'periodicity': 'monthly',
            'year': cls.test_date.strftime('%Y'),
            'month': cls.test_date.strftime('%m'),
        })

    def test_gstr2b(self):

        gstr2b_json = self._read_mock_json('gstr2b_response.json')
        self.report.gstr2b_json_from_portal_ids = self.env['ir.attachment'].create({
            'name': 'gstr2b.json',
            'mimetype': 'application/json',
            'raw': json.dumps(gstr2b_json),
        })
        self.report.gstr2b_match_data()

        self.assertEqual(self.report.gstr2b_status, "partially_matched")
        self.assertEqual(self.fully_matched_bill.l10n_in_gstr2b_reconciliation_status, "matched")
        self.assertEqual(bool(self.fully_matched_bill.l10n_in_exception), False)
        self.assertEqual(self.fully_matched_bill_refund.l10n_in_gstr2b_reconciliation_status, "matched")
        self.assertEqual(self.bill_with_conflict_date.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_date_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")

        self.assertEqual(self.bill_with_conflict_type.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_type_date.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_type_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_type_date_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")

        self.assertEqual(self.bill_with_conflict_vat.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_date.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_date_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")

        self.assertEqual(self.bill_with_conflict_vat_type.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_type_date.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_type_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")
        self.assertEqual(self.bill_with_conflict_vat_type_date_amount.l10n_in_gstr2b_reconciliation_status, "partially_matched")

        self.assertEqual(self.bill_not_in_gstr2b.l10n_in_gstr2b_reconciliation_status, "bills_not_in_gstr2")
        self.assertEqual(self.overseas_bill.l10n_in_gstr2b_reconciliation_status, "matched")
        bill_not_in_odoo = self.env['account.move'].search([('ref', '=', '533515'), ('company_id', '=', self.default_company.id)])
        self.assertEqual(len(bill_not_in_odoo), 1)
        self.assertEqual(bill_not_in_odoo.l10n_in_gstr2b_reconciliation_status, 'gstr2_bills_not_in_odoo')
        self.assertEqual(bill_not_in_odoo.l10n_in_gst_treatment, 'regular')
        sez_bill = self.env['account.move'].search([('ref', '=', 'SEZ/123'), ('company_id', '=', self.default_company.id)])
        self.assertEqual(len(sez_bill), 1)
        self.assertEqual(sez_bill.l10n_in_gstr2b_reconciliation_status, "gstr2_bills_not_in_odoo")
        self.assertEqual(bool(sez_bill.l10n_in_exception), False)
        self.assertEqual(sez_bill.l10n_in_gst_treatment, "special_economic_zone")
