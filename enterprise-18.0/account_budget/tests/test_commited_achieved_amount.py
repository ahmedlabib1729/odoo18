# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .common import TestAccountBudgetCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestCommittedAchievedAmount(TestAccountBudgetCommon):

    def create_other_category_aal(self):
        self.env['account.analytic.line'].create({
            'name': 'aal 1',
            'date': '2019-01-10',
            self.project_column_name: self.analytic_account_partner_a.id,
            'amount': 200,
        })
        self.env['account.analytic.line'].create({
            'name': 'aal 2',
            'date': '2019-01-10',
            self.project_column_name: self.analytic_account_partner_b.id,
            'amount': 200,
        })
        self.env['account.analytic.line'].create({
            'name': 'aal 3',
            'date': '2019-01-10',
            self.project_column_name: self.analytic_account_partner_a.id,
            'amount': -100,
        })
        self.env['account.analytic.line'].create({
            'name': 'aal 4',
            'date': '2019-01-10',
            self.project_column_name: self.analytic_account_partner_b.id,
            'amount': -100,
        })

    def test_budget_revenue_committed_achieved_amount(self):
        plan_a_line, plan_b_line, plan_b_admin_line = self.budget_analytic_revenue.budget_line_ids
        self.assertEqual(plan_a_line.achieved_amount, 0)
        self.assertEqual(plan_b_line.achieved_amount, 0)
        self.assertEqual(plan_b_admin_line.achieved_amount, 0)
        bill = self.purchase_order.invoice_ids

        # Post Purchase order's bill also to make sure this doesn't affect the revenue budget
        (bill + self.out_invoice).action_post()

        self.env['purchase.order'].invalidate_model(['currency_rate'])
        self.env['purchase.order.line'].invalidate_model(['qty_received', 'qty_invoiced', 'price_unit'])
        self.env['budget.line'].invalidate_model(['achieved_amount', 'committed_amount'])
        self.create_other_category_aal()

        # 3 positive analytic lines with analytic_account_partner_a:
        # invoice line[0]: 200, invoice line[1]: 400, aal 1: 200
        # Total Achieved = 800
        self.assertEqual(plan_a_line.achieved_amount, 800.0)
        # Committed should be same as budget type is revenue
        self.assertEqual(plan_a_line.committed_amount, 800.0)

        # 3 positive analytic lines with analytic_account_partner_b:
        # invoice line[2]: 700, invoice line[3]: 600, aal 2: 200
        # Total Achieved = 1500
        self.assertEqual(plan_b_line.achieved_amount, 1500.0)
        # Committed should be same as budget type is revenue
        self.assertEqual(plan_b_line.committed_amount, 1500.0)

        # 1 positive analytic line with accounts analytic_account_partner_b and analytic_account_administratif
        # invoice line[3]: 600
        self.assertEqual(plan_b_admin_line.achieved_amount, 600.0)
        # Committed should be same as budget type is revenue
        self.assertEqual(plan_b_admin_line.committed_amount, 600.0)

    def test_budget_analytic_expense_committed_achieved_amount(self):
        plan_a_line, plan_b_line, plan_b_admin_line = self.budget_analytic_expense.budget_line_ids
        self.assertEqual(plan_a_line.achieved_amount, 0)
        self.assertEqual(plan_b_line.achieved_amount, 0)
        self.assertEqual(plan_b_admin_line.achieved_amount, 0)
        bill = self.purchase_order.invoice_ids
        bill.write({'invoice_date': '2019-01-10'})
        bill.action_post()

        self.env['purchase.order'].invalidate_model(['currency_rate'])
        self.env['purchase.order.line'].invalidate_model(['qty_received', 'qty_invoiced', 'price_unit'])
        self.env['budget.line'].invalidate_model(['achieved_amount', 'committed_amount'])
        self.create_other_category_aal()

        # 3 negative analytic lines with account analytic_account_partner_a:
        # Bill line[0]: -100, line[1]: -300, aal 3: -100
        # Total Achieved = 500
        self.assertEqual(plan_a_line.achieved_amount, 500.0)

        # Product A have 2 PO lines, one for line[0] with 10 order and 1 received and one for line[1] with 10 order and 3 received with account analytic_account_partner_a
        # Committed = ((order - received) * price) + achieved = ((10-1) + (10-3)) * 100 + 500 = 2100
        self.assertEqual(plan_a_line.committed_amount, 2100.0)

        # 3 negative analytic lines with account analytic_account_partner_b:
        # Bill line[2]: -600, line[3]: -500, aal 4: -100
        # Total Achieved = 1200
        self.assertEqual(plan_b_line.achieved_amount, 1200.0)

        # Product B have 2 PO lines, one for line[2] with 10 order and 6 received and one for line[3] with 10 order and 5 received with account analytic_account_partner_b
        # Committed = ((order - received) * price) + achieved = ((10-6) + (10-5)) * 100 + 1200 = 2100
        self.assertEqual(plan_b_line.committed_amount, 2100.0)

        # 1 negative analytic line with accounts analytic_account_partner_b and analytic_account_administratif
        # Bill line[3]: -500,
        self.assertEqual(plan_b_admin_line.achieved_amount, 500.0)

        # Product B have 1 PO line line[3] with 10 order and 5 received with analytic_account_partner_b and analytic_account_administratif
        # Committed = ((order - received) * price) + achieved = ((10-5) * 100 + 500 = 1000
        self.assertEqual(plan_b_admin_line.committed_amount, 1000.0)

    def test_budget_analytic_both_committed_achieved_amount(self):
        plan_a_line, plan_b_line, plan_b_admin_line = self.budget_analytic_both.budget_line_ids
        self.assertEqual(plan_a_line.achieved_amount, 0)
        self.assertEqual(plan_b_line.achieved_amount, 0)
        self.assertEqual(plan_b_admin_line.achieved_amount, 0)
        bill = self.purchase_order.invoice_ids
        bill.write({'invoice_date': '2019-01-10'})

        (bill + self.out_invoice).action_post()

        self.env['purchase.order'].invalidate_model(['currency_rate'])
        self.env['purchase.order.line'].invalidate_model(['qty_received', 'qty_invoiced', 'price_unit'])
        self.env['budget.line'].invalidate_model(['achieved_amount', 'committed_amount'])
        self.create_other_category_aal()

        # 3 Negative and 3 Positive analytic lines positive with account analytic_account_partner_a:
        # Bill line[0]: -100, line[1]: -300, Invoice line[0]: 200, line[1]: 400, aal 1: 200, aal 3: -100
        # Total Achieved = (-100 + (-300) + 200 + 400 + 200 + (-100)) = 300
        self.assertEqual(plan_a_line.achieved_amount, 300)

        # Product A have 2 PO lines, one for line[0] with 10 order and 1 received and one for line[1] with 10 order and 3 received with account analytic_account_partner_a
        # Committed = ((order - received) * price) + achieved = ((10-1) + (10-3)) * 100 + 300 = 1900
        self.assertEqual(plan_a_line.committed_amount, 1900.0)

        # 3 Negative and 3 Positive analytic lines positive with account analytic_account_partner_a:
        # Bill line[2]: -600, line[3]: -500, Out Invoice line[2]: 700, line[3]: 600, aal 2: 200, aal 4: -100
        # Total Achieved = ((-600) + (-500) + 700 + 600 + 200 + (-100)) = 300
        self.assertEqual(plan_b_line.achieved_amount, 300)

        # Product B have 2 PO lines, one for line[2] with 10 order and 6 received and one for line[3] with 10 order and 5 received with account analytic_account_partner_b
        # Committed = ((order - received) * price) + achieved = ((10-6) + (10-5)) * 100 + 300 = 1200
        self.assertEqual(plan_b_line.committed_amount, 1200)

        # 1 Negative and 1 Positive lines with accounts analytic_account_partner_b and analytic_account_administratif
        # Bill line[3]: -500 Out Bill line[3]: 600
        # Total Achieved = ((-500) + 600) = 100
        self.assertEqual(plan_b_admin_line.achieved_amount, 100)

        # Product B have 1 PO line line[3] with 10 order and 5 received with analytic_account_partner_b and analytic_account_administratif
        # Committed = ((order - received) * price) + achieved = ((10-5) * 100 + 100 = 600
        self.assertEqual(plan_b_admin_line.committed_amount, 600)
