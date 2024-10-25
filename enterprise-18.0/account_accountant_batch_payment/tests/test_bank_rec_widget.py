# -*- coding: utf-8 -*-
from unittest.mock import patch

from odoo import Command
from odoo.addons.account_accountant.tests.test_bank_rec_widget_common import TestBankRecWidgetCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestBankRecWidgetWithoutEntry(TestBankRecWidgetCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_method_line = cls.company_data['default_journal_bank'].inbound_payment_method_line_ids\
            .filtered(lambda l: l.code == 'batch_payment')

    def test_state_changes(self):
        invoice = self.init_invoice('out_invoice', partner=self.partner_a, amounts=[1000.0], post=True)
        invoice_payment = self.env['account.payment.register'].create({
            'payment_date': '2019-01-01',
            'payment_method_line_id': self.payment_method_line.id,
            'line_ids': [Command.set(invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term').ids)],
        })._create_payments()
        from_scratch_payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'amount': 1000,
        })
        from_scratch_payment.action_post()
        for payment, expect_reconcile in [(invoice_payment, True), (from_scratch_payment, False)]:
            self.assertFalse(payment.move_id)
            batch = self.env['account.batch.payment'].create({
                'journal_id': self.company_data['default_journal_bank'].id,
                'payment_ids': [Command.set(payment.ids)],
                'payment_method_id': self.payment_method_line.payment_method_id.id,
            })
            batch.validate_batch()
            self.assertRecordValues(payment, [{
                'state': 'in_process',
                'is_sent': True,
            }])
            self.assertRecordValues(batch, [{'state': 'sent'}])

            st_line = self._create_st_line(1000.0, payment_ref=batch.name, partner_id=self.partner_a.id)
            wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
            wizard._action_add_new_batch_payments(batch)
            self.assertRecordValues(wizard.line_ids, [
                # pylint: disable=C0326
                {'flag': 'liquidity',       'balance':  1000.0},
                {'flag': 'new_batch',       'balance': -1000.0},
            ])
            wizard._action_validate()

            self.assertRecordValues(st_line.move_id.line_ids, [
                {'account_id': self.partner_a.property_account_receivable_id.id, 'balance': -1000.0, 'reconciled': expect_reconcile},
                {'account_id': st_line.journal_id.default_account_id.id,         'balance':  1000.0, 'reconciled': False},
            ])
            self.assertRecordValues(payment, [{
                'state': 'paid',
                'is_sent': True,
            }])
            self.assertRecordValues(batch, [{'state': 'reconciled'}])

    def test_writeoff(self):
        invoice = self.init_invoice('out_invoice', partner=self.partner_a, amounts=[1000.0], post=True)
        payment = self.env['account.payment.register'].create({
            'payment_date': '2019-01-01',
            'payment_method_line_id': self.payment_method_line.id,
            'line_ids': [Command.set(invoice.line_ids.filtered(lambda l: l.display_type == 'payment_term').ids)],
        })._create_payments()
        batch = self.env['account.batch.payment'].create({
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_ids': [Command.set(payment.ids)],
            'payment_method_id': self.payment_method_line.payment_method_id.id,
        })
        batch.validate_batch()

        st_line = self._create_st_line(900.0, payment_ref=batch.name, partner_id=self.partner_a.id)
        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
        wizard._action_add_new_batch_payments(batch)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'balance':   900.0},
            {'flag': 'new_batch',       'balance': -1000.0},
            {'flag': 'auto_balance',    'balance':   100.0},
        ])
        line = wizard.line_ids.filtered(lambda l: l.flag == 'auto_balance')
        wizard._js_action_mount_line_in_edit(line.index)
        wizard._js_action_line_set_partner_receivable_account(line.index)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'balance':   900.0},
            {'flag': 'new_batch',       'balance': -1000.0},
            {'flag': 'manual',          'balance':   100.0},
        ])
        wizard._action_validate()

        self.assertRecordValues(st_line.move_id.line_ids, [
            {'account_id': self.partner_a.property_account_receivable_id.id, 'balance': -1000.0, 'reconciled': True},
            {'account_id': st_line.journal_id.default_account_id.id,         'balance':   900.0, 'reconciled': False},
            {'account_id': self.partner_a.property_account_receivable_id.id, 'balance':   100.0, 'reconciled': False},
        ])

    def test_multiple_exchange_diffs_in_batch(self):
        # Create a statement line when the currency rate is 1 USD == 2 EUR == 4 CAD
        st_line = self._create_st_line(
            1000.0,
            partner_id=self.partner_a.id,
            date='2017-01-01'
        )
        inv_line = self._create_invoice_line(
            'out_invoice',
            partner_id=self.partner_a.id,
            invoice_line_ids=[{'price_unit': 5000.0, 'tax_ids': []}],
        )
        # Payment when 1 USD == 1 EUR
        payment_eur_gain_diff = self.env['account.payment'].create({
            'date': '2015-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 100.0,
        })
        # Payment when 1 USD == 1 EUR
        payment_eur_gain_diff_2 = self.env['account.payment'].create({
            'date': '2015-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 200.0,
        })
        # Payment when 1 USD == 3 EUR
        payment_eur_loss_diff = self.env['account.payment'].create({
            'date': '2016-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 240.0,
        })
        # Payment when 1 USD == 6 CAD
        payment_cad_loss_diff = self.env['account.payment'].create({
            'date': '2016-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency_2.id,
            'amount': 300.0,
        })
        payments = payment_eur_gain_diff + payment_eur_gain_diff_2 + payment_eur_loss_diff + payment_cad_loss_diff
        payments.action_post()

        batch = self.env['account.batch.payment'].create({
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_ids': [Command.set(payments.ids)],
            'payment_method_id': self.payment_method_line.payment_method_id.id,
        })

        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
        wizard._action_add_new_amls(inv_line)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'balance': 1000.0},
            {'flag': 'new_aml',         'balance': -1000.0},
        ])

        wizard._action_add_new_batch_payments(batch)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'amount_currency': 1000.0,     'balance': 1000.0},
            {'flag': 'new_aml',         'amount_currency': -655.0,     'balance': -655.0},
            {'flag': 'new_batch',       'amount_currency': -840.0,     'balance': -430.0},
            {'flag': 'exchange_diff',   'amount_currency':    0.0,     'balance':  150.0},
            {'flag': 'exchange_diff',   'amount_currency':    0.0,     'balance':  -40.0},
            {'flag': 'exchange_diff',   'amount_currency':    0.0,     'balance':  -25.0},
        ])

        wizard._js_action_validate()
        self.assertRecordValues(st_line.move_id.line_ids, [
            {'balance':   -270.0, 'amount_currency':   -540.0, 'amount_residual':   -270.0},
            {'balance':    -75.0, 'amount_currency':   -300.0, 'amount_residual':    -75.0},
            {'balance':   1000.0, 'amount_currency':   1000.0, 'amount_residual':   1000.0},
            {'balance':   -655.0, 'amount_currency':   -655.0, 'amount_residual':      0.0},
        ])

        reconciled = st_line.move_id.line_ids.matched_debit_ids.debit_move_id | st_line.move_id.line_ids.matched_credit_ids.credit_move_id
        self.assertRecordValues(reconciled, [
            {'balance':   5000.0, 'amount_currency':   5000.0, 'amount_residual':   4345.0},
        ])


@tagged('post_install', '-at_install')
class TestBankRecWidgetWithEntry(TestBankRecWidgetCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_method_line = cls.company_data['default_journal_bank'].inbound_payment_method_line_ids\
            .filtered(lambda l: l.code == 'batch_payment')
        cls.payment_method_line.payment_account_id = cls.inbound_payment_method_line.payment_account_id

    def test_matching_batch_payment(self):
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'amount': 100.0,
        })
        payment.action_post()

        batch = self.env['account.batch.payment'].create({
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_ids': [Command.set(payment.ids)],
            'payment_method_id': self.payment_method_line.payment_method_id.id,
        })
        self.assertRecordValues(batch, [{'state': 'draft'}])

        # Validate the batch and print it.
        batch.validate_batch()
        batch.print_batch_payment()
        self.assertRecordValues(batch, [{'state': 'sent'}])

        st_line = self._create_st_line(1000.0, payment_ref=f"turlututu {batch.name} tsointsoin", partner_id=self.partner_a.id)

        # Create a rule matching the batch payment.
        self.env['account.reconcile.model'].search([('company_id', '=', self.company_data['company'].id)]).unlink()
        rule = self._create_reconcile_model()

        # Ensure the rule matched the batch.
        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
        wizard._action_trigger_matching_rules()

        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'balance': 1000.0,  'reconcile_model_id': False},
            {'flag': 'new_aml',         'balance': -100.0,  'reconcile_model_id': rule.id},
            {'flag': 'auto_balance',    'balance': -900.0,  'reconcile_model_id': False},
        ])
        self.assertRecordValues(wizard, [{
            'state': 'valid',
        }])
        wizard._action_validate()

        self.assertRecordValues(batch, [{'state': 'reconciled'}])
        self.assertRecordValues(st_line.move_id.line_ids, [
            {'account_id': st_line.journal_id.default_account_id.id,         'balance': 1000.0, 'reconciled': False},
            {'account_id': payment.outstanding_account_id.id,                'balance': -100.0, 'reconciled': True},
            {'account_id': self.partner_a.property_account_receivable_id.id, 'balance': -900.0, 'reconciled': False},
        ])

    def test_single_payment_from_batch_on_bank_reco_widget(self):
        payments = self.env['account.payment'].create([
            {
                'date': '2018-01-01',
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.partner_a.id,
                'payment_method_line_id': self.payment_method_line.id,
                'amount': i * 100.0,
            }
            for i in range(1, 4)
        ])
        payments.action_post()

        # Add payments to a batch.
        batch_payment = self.env['account.batch.payment'].create({
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_ids': [Command.set(payments.ids)],
            'payment_method_id': self.payment_method_line.payment_method_id.id,
        })

        st_line = self._create_st_line(100.0, partner_id=self.partner_a.id)
        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
        # Add payment1 from the aml tab
        aml = payments[0].move_id.line_ids.filtered(lambda x: x.account_id.account_type != 'asset_receivable')
        wizard._action_add_new_amls(aml)

        # Validate with one payment inside a batch should reconcile directly the statement line.
        wizard._js_action_validate()
        self.assertTrue(wizard.return_todo_command)
        self.assertTrue(wizard.return_todo_command.get('done'))

        self.assertEqual(batch_payment.amount_residual, sum(payments[1:].mapped('amount')), "The batch amount should change following payment reconciliation")

    def test_multiple_exchange_diffs_in_batch(self):
        # Create a statement line when the currency rate is 1 USD == 2 EUR == 4 CAD
        st_line = self._create_st_line(
            1000.0,
            partner_id=self.partner_a.id,
            date='2017-01-01'
        )
        inv_line = self._create_invoice_line(
            'out_invoice',
            partner_id=self.partner_a.id,
            invoice_line_ids=[{'price_unit': 5000.0, 'tax_ids': []}],
        )
        # Payment when 1 USD == 1 EUR
        payment_eur_gain_diff = self.env['account.payment'].create({
            'date': '2015-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 100.0,
        })
        # Payment when 1 USD == 1 EUR
        payment_eur_gain_diff_2 = self.env['account.payment'].create({
            'date': '2015-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 200.0,
        })
        # Payment when 1 USD == 3 EUR
        payment_eur_loss_diff = self.env['account.payment'].create({
            'date': '2016-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency.id,
            'amount': 240.0,
        })
        # Payment when 1 USD == 6 CAD
        payment_cad_loss_diff = self.env['account.payment'].create({
            'date': '2016-01-01',
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner_a.id,
            'payment_method_line_id': self.payment_method_line.id,
            'currency_id': self.other_currency_2.id,
            'amount': 300.0,
        })
        payments = payment_eur_gain_diff + payment_eur_gain_diff_2 + payment_eur_loss_diff + payment_cad_loss_diff
        payments.action_post()

        self.assertRecordValues(payments.move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current'), [
            {'balance': 100.0, 'amount_currency': 100.0, 'amount_residual': 100.0},
            {'balance': 200.0, 'amount_currency': 200.0, 'amount_residual': 200.0},
            {'balance':  80.0, 'amount_currency': 240.0, 'amount_residual':  80.0},
            {'balance':  50.0, 'amount_currency': 300.0, 'amount_residual':  50.0},
        ])

        batch = self.env['account.batch.payment'].create({
            'journal_id': self.company_data['default_journal_bank'].id,
            'payment_ids': [Command.set(payments.ids)],
            'payment_method_id': self.payment_method_line.payment_method_id.id,
        })

        wizard = self.env['bank.rec.widget'].with_context(default_st_line_id=st_line.id).new({})
        wizard._action_add_new_amls(inv_line)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'balance': 1000.0},
            {'flag': 'new_aml',         'balance': -1000.0},
        ])

        wizard._action_add_new_batch_payments(batch)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'amount_currency': 1000.0,     'balance': 1000.0},
            {'flag': 'new_aml',         'amount_currency': -655.0,     'balance': -655.0},
            {'flag': 'new_batch',       'amount_currency': -840.0,     'balance': -430.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': 150.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': -40.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': -25.0},
        ])

        wizard._action_expand_batch_payments(batch)
        self.assertRecordValues(wizard.line_ids, [
            # pylint: disable=C0326
            {'flag': 'liquidity',       'amount_currency': 1000.0,     'balance': 1000.0},
            {'flag': 'new_aml',         'amount_currency': -655.0,     'balance': -655.0},
            {'flag': 'new_aml',         'amount_currency': -100.0,     'balance': -100.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': 50.0},
            {'flag': 'new_aml',         'amount_currency': -200.0,     'balance': -200.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': 100.0},
            {'flag': 'new_aml',         'amount_currency': -240.0,     'balance': -80.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': -40.0},
            {'flag': 'new_aml',         'amount_currency': -300.0,     'balance': -50.0},
            {'flag': 'exchange_diff',   'amount_currency': 0.0,        'balance': -25.0},
        ])

        wizard._js_action_validate()
        A, B, C, D, E, F = st_line.move_id.line_ids.mapped('matching_number')
        self.assertRecordValues(st_line.move_id.line_ids, [
            {'balance':   1000.0, 'amount_currency':   1000.0, 'amount_residual':   1000.0, 'matching_number': A},
            {'balance':   -655.0, 'amount_currency':   -655.0, 'amount_residual':      0.0, 'matching_number': B},
            {'balance':    -50.0, 'amount_currency':   -100.0, 'amount_residual':      0.0, 'matching_number': C},
            {'balance':   -100.0, 'amount_currency':   -200.0, 'amount_residual':      0.0, 'matching_number': D},
            {'balance':   -120.0, 'amount_currency':   -240.0, 'amount_residual':      0.0, 'matching_number': E},
            {'balance':    -75.0, 'amount_currency':   -300.0, 'amount_residual':      0.0, 'matching_number': F},
        ])

        reconciled = st_line.move_id.line_ids.matched_debit_ids.debit_move_id | st_line.move_id.line_ids.matched_credit_ids.credit_move_id
        self.assertRecordValues(reconciled, [
            {'balance':   5000.0, 'amount_currency':   5000.0, 'amount_residual':   4345.0, 'matching_number': B},
            {'balance':    100.0, 'amount_currency':    100.0, 'amount_residual':      0.0, 'matching_number': C},
            {'balance':    200.0, 'amount_currency':    200.0, 'amount_residual':      0.0, 'matching_number': D},
            {'balance':     40.0, 'amount_currency':      0.0, 'amount_residual':      0.0, 'matching_number': E},
            {'balance':     80.0, 'amount_currency':    240.0, 'amount_residual':      0.0, 'matching_number': E},
            {'balance':     25.0, 'amount_currency':      0.0, 'amount_residual':      0.0, 'matching_number': F},
            {'balance':     50.0, 'amount_currency':    300.0, 'amount_residual':      0.0, 'matching_number': F},
        ])
        self.assertRecordValues(payments.move_id.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_current'), [
            {'balance':    100.0, 'amount_currency':    100.0, 'amount_residual':      0.0},
            {'balance':    200.0, 'amount_currency':    200.0, 'amount_residual':      0.0},
            {'balance':     80.0, 'amount_currency':    240.0, 'amount_residual':      0.0},
            {'balance':     50.0, 'amount_currency':    300.0, 'amount_residual':      0.0},
        ])
