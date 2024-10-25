# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models
from odoo.tools import SQL


class BudgetLine(models.Model):
    _name = 'budget.line'
    _inherit = 'analytic.plan.fields.mixin'
    _description = "Budget Line"
    _order = 'sequence, id'

    name = fields.Char(related='budget_analytic_id.name', string='Budget Name')
    sequence = fields.Integer('Sequence', default=10)
    budget_analytic_id = fields.Many2one('budget.analytic', 'Budget Analytic', ondelete='cascade', index=True, required=True)
    date_from = fields.Date('Start Date', related='budget_analytic_id.date_from', store=True)
    date_to = fields.Date('End Date', related='budget_analytic_id.date_to', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    budget_amount = fields.Monetary(
        string='Budgeted')
    achieved_amount = fields.Monetary(
        compute='_compute_all',
        string='Achieved',
        help="Amount Billed/Invoiced.")
    achieved_percentage = fields.Float(
        compute='_compute_all',
        string='Achieved (%)')
    committed_amount = fields.Monetary(
        compute='_compute_all',
        string='Committed',
        help="Already Billed amount + Confirmed purchase orders.")
    committed_percentage = fields.Float(
        compute='_compute_all',
        string='Committed (%)')
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount',
        string='Theoretical',
        help="Amount supposed to be Billed/Invoiced, formula = (Budget Amount / Budget Days) x Budget Days Completed")
    theoritical_percentage = fields.Float(
        compute='_compute_theoritical_amount',
        string='Theoretical (%)',
        aggregator='avg')
    company_id = fields.Many2one(related='budget_analytic_id.company_id', comodel_name='res.company', string='Company', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_compute_above_budget')
    budget_analytic_state = fields.Selection(related='budget_analytic_id.state', string='Budget State', store=True, readonly=True)

    @api.depends('achieved_amount', 'budget_amount')
    def _compute_above_budget(self):
        for line in self:
            line.is_above_budget = line.achieved_amount > line.budget_amount

    def _compute_all(self):
        self.env['purchase.order'].flush_model()
        self.env['purchase.order.line'].flush_model()

        def get_line_query(line):
            account_ids = {fname: line[fname].id for fname in account_fname if line[fname]}
            fnames = list(account_ids.keys())
            budget_type = line.budget_analytic_id.budget_type
            company_id = line.budget_analytic_id.company_id.id
            date_from = line.date_from
            date_to = line.date_to
            if budget_type == 'expense':
                aal_amount_condition = SQL('aal.amount < 0')
            elif budget_type == 'revenue':
                aal_amount_condition = SQL('aal.amount > 0')
            else:
                aal_amount_condition = SQL('TRUE')
            if budget_type != 'revenue':
                purchase_order_query = SQL(
                    """SELECT (pol.product_qty - pol.qty_invoiced) / po.currency_rate * pol.price_unit::FLOAT * (a.rate)::FLOAT AS committed,
                               0 AS achieved,
                               %(pod_fields)s
                          FROM purchase_order_line pol
                          JOIN purchase_order po ON pol.order_id = po.id
                    CROSS JOIN JSONB_TO_RECORDSET(pol.analytic_json) AS a(rate FLOAT, %(json_table)s)
                         WHERE po.date_order >= %(date_from)s
                           AND po.date_order <= %(date_to)s
                           AND pol.qty_invoiced < pol.product_qty
                           AND po.company_id = %(company_id)s
                           AND po.state in ('purchase', 'done')
                           AND %(pod_condition)s
                    """,
                    date_from=date_from,
                    date_to=date_to,
                    company_id=company_id,
                    json_table=SQL(', ').join(SQL("%s INT", SQL.identifier(fname)) for fname in account_fname),
                    pod_fields=SQL(', ').join(self._field_to_sql('a', fname) for fname in account_fname),
                    pod_condition=SQL(' AND ').join(SQL('%s = %s', self._field_to_sql('a', fname), account_ids[fname]) for fname in fnames) or SQL('FALSE'),
                )
            else:
                purchase_order_query = SQL(
                    """SELECT 0 AS committed,
                               0 AS achieved
                    """
                )

            query = SQL(
                """(
                    WITH purchase_order_data AS (%(purchase_order_query)s),
                    account_analytic_line_data AS (
                        SELECT 0 AS committed,
                               aal.amount AS achieved,
                               %(aal_fields)s
                          FROM account_analytic_line aal
                         WHERE aal.date >= %(date_from)s
                           AND aal.date <= %(date_to)s
                           AND aal.company_id = %(company_id)s
                           AND %(all_conditions)s
                           AND %(aal_amount_condition)s
                    )
                    SELECT %(line_id)s as id,
                           COALESCE(SUM(pod.committed), 0) + COALESCE(SUM(aal.committed), 0) AS committed,
                           COALESCE(SUM(pod.achieved), 0) + COALESCE(SUM(aal.achieved), 0) AS achieved
                      FROM purchase_order_data pod
                 FULL JOIN account_analytic_line_data aal ON %(join_condition)s
                )""",
                line_id=line.id,
                date_from=date_from,
                date_to=date_to,
                company_id=company_id,
                aal_fields=SQL(', ').join(self._field_to_sql('aal', fname) for fname in account_fname),
                all_conditions=SQL(' AND ').join(SQL('%s = %s', self._field_to_sql('aal', fname), account_ids[fname]) for fname in fnames) or SQL('FALSE'),
                join_condition=budget_type == 'expense' and SQL(' AND ').join(SQL('%s = %s', self._field_to_sql('pod', fname), self._field_to_sql('aal', fname)) for fname in account_fname) or SQL('FALSE'),
                aal_amount_condition=aal_amount_condition,
                purchase_order_query=purchase_order_query
            )
            return query

        project_plan, other_plans = self.env['account.analytic.plan']._get_all_plans()
        account_fname = [plan._column_name() for plan in project_plan + other_plans]
        queries = [get_line_query(line) for line in self.filtered('id')]
        result = {}
        if queries:
            self.env.cr.execute(SQL(
                "SELECT * FROM (%s) AS combined_results",
                SQL(" UNION ALL ").join(queries),
            ))
            result = {line['id']: line for line in self.env.cr.dictfetchall()}

        for line in self:
            sign = -1 if line.budget_analytic_id.budget_type == 'expense' else 1
            if line.id not in result:
                committed = achieved = 0.0
            else:
                committed = result[line.id]['committed']
                achieved = result[line.id]['achieved']
            line.committed_amount = committed + achieved * sign
            line.achieved_amount = achieved * sign
            line.committed_percentage = line.budget_amount and (line.committed_amount / line.budget_amount)
            line.achieved_percentage = line.budget_amount and (line.achieved_amount / line.budget_amount)

    @api.depends('date_from', 'date_to')
    def _compute_theoritical_amount(self):
        today = fields.Date.context_today(self)
        for line in self:
            if not line.date_from or not line.date_to:
                line.theoritical_amount = 0
                line.theoritical_percentage = 0
                continue
            # One day is added since we need to include the start and end date in the computation.
            # For example, between April 1st and April 30th, the timedelta must be 30 days.
            line_timedelta = line.date_to - line.date_from + timedelta(days=1)
            elapsed_timedelta = min(max(today, line.date_from), line.date_to) - line.date_from + timedelta(days=1)
            line.theoritical_amount = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.budget_amount
            line.theoritical_percentage = line.budget_amount and (line.theoritical_amount / line.budget_amount)

    def _read_group_select(self, aggregate_spec, query):
        # flag achieved_amount/theoritical_amount as aggregatable
        # and manually sum the values from the records in the group
        if aggregate_spec in ('achieved_amount:sum', 'theoritical_amount:sum', 'theoritical_percentage:avg'):
            return super()._read_group_select('id:recordset', query)
        return super()._read_group_select(aggregate_spec, query)

    def _read_group_postprocess_aggregate(self, aggregate_spec, raw_values):
        if aggregate_spec in ('achieved_amount:sum', 'theoritical_amount:sum', 'theoritical_percentage:avg'):
            field_name, op = aggregate_spec.split(':')
            column = super()._read_group_postprocess_aggregate('id:recordset', raw_values)
            if op == 'sum':
                return (sum(records.mapped(field_name)) for records in column)
            if op == 'avg':
                return (sum(records.mapped(field_name)) / len(records) for records in column)
        return super()._read_group_postprocess_aggregate(aggregate_spec, raw_values)

    def action_open_budget_entries(self):
        project_plan, other_plans = self.env['account.analytic.plan']._get_all_plans()
        all_plan = project_plan + other_plans
        domain = [('budget_analytic_id', '=', self.budget_analytic_id.id)]
        for plan in all_plan:
            fname = plan._column_name()
            if self[fname]:
                domain += [(fname, 'in', self[fname].ids)]
        action = self.env['ir.actions.act_window']._for_xml_id('account_budget.budget_report_action')
        action['domain'] = domain
        return action
