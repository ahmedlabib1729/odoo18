# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
from odoo.tools import SQL


class BudgetReport(models.Model):
    _name = 'budget.report'
    _inherit = 'analytic.plan.fields.mixin'
    _description = "Budget Report"
    _auto = False
    _order = False

    date = fields.Date('Date')
    res_model = fields.Char('Model', readonly=True)
    res_id = fields.Many2oneReference('Document', model_field='res_model', readonly=True)
    description = fields.Char('Description', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    line_type = fields.Selection([('budget', 'Budget'), ('committed', 'Committed'), ('achieved', 'Achieved')], 'Type', readonly=True)
    budget = fields.Float('Budget', readonly=True)
    committed = fields.Float('Committed', readonly=True)
    achieved = fields.Float('Achieved', readonly=True)
    budget_analytic_id = fields.Many2one('budget.analytic', 'Budget Analytic', readonly=True)

    def _get_bl_query(self, plan_fnames):
        return SQL(
            """
            SELECT CONCAT('bl', bl.id::TEXT) AS id,
                   bl.budget_analytic_id AS budget_analytic_id,
                   'budget.analytic' AS res_model,
                   bl.budget_analytic_id AS res_id,
                   bl.date_from AS date,
                   ba.name AS description,
                   bl.company_id AS company_id,
                   NULL AS user_id,
                   'budget' AS line_type,
                   bl.budget_amount AS budget,
                   0 AS committed,
                   0 AS achieved,
                   %(plan_fields)s
              FROM budget_line bl
              JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
            """,
            plan_fields=SQL(', ').join(self.env['budget.line']._field_to_sql('bl', fname) for fname in plan_fnames)
        )

    def _get_aal_query(self, plan_fnames):
        return SQL(
            """
            SELECT CONCAT('aal', aal.id::TEXT) AS id,
                   budget.id AS budget_analytic_id,
                   'account.analytic.line' AS res_model,
                   aal.id AS res_id,
                   aal.date AS date,
                   aal.name AS description,
                   aal.company_id AS company_id,
                   aal.user_id AS user_id,
                   'achieved' AS line_type,
                   0 AS budget,
                   aal.amount * budget.sign AS committed,
                   aal.amount * budget.sign AS achieved,
                   %(analytic_fields)s
              FROM account_analytic_line aal
 LEFT JOIN LATERAL (
                        SELECT DISTINCT ON (id)
                               ba.id,
                               CASE WHEN ba.budget_type = 'expense' THEN -1 ELSE 1 END AS sign
                          FROM budget_line bl
                          JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id
                         WHERE aal.date >= bl.date_from
                           AND aal.date <= bl.date_to
                           AND aal.company_id = bl.company_id
                           AND %(condition)s
                           AND (
                               CASE
                                   WHEN ba.budget_type = 'expense' THEN aal.amount < 0
                                   WHEN ba.budget_type = 'revenue' THEN aal.amount > 0
                                   ELSE TRUE
                               END
                           )
                   ) AS budget ON TRUE
            """,
            analytic_fields=SQL(', ').join(self.env['account.analytic.line']._field_to_sql('aal', fname) for fname in plan_fnames),
            condition=SQL(' AND ').join(SQL(
                "%(bl)s IS NULL OR %(aal)s = %(bl)s",
                bl=self.env['budget.line']._field_to_sql('bl', fname),
                aal=self.env['budget.line']._field_to_sql('aal', fname),
            ) for fname in plan_fnames)
        )

    def _get_pol_query(self, plan_fnames):
        return SQL(
            """
            SELECT (pol.id::TEXT || '-' || ROW_NUMBER() OVER (PARTITION BY pol.id ORDER BY pol.id)) AS id,
                   budget.id AS budget_analytic_id,
                   'purchase.order' AS res_model,
                   po.id AS res_id,
                   po.date_order AS date,
                   pol.name AS description,
                   pol.company_id AS company_id,
                   po.user_id AS user_id,
                   'committed' AS line_type,
                   0 AS budget,
                   (pol.product_qty - pol.qty_invoiced) / po.currency_rate * pol.price_unit::FLOAT * (a.rate)::FLOAT AS committed,
                   0 AS achieved,
                   %(analytic_fields)s
              FROM purchase_order_line pol
              JOIN purchase_order po ON pol.order_id = po.id AND po.state in ('purchase', 'done')
        CROSS JOIN JSONB_TO_RECORDSET(pol.analytic_json) AS a(rate FLOAT, %(field_cast)s)
 LEFT JOIN LATERAL (
                       SELECT DISTINCT ba.id
                         FROM budget_line bl
                         JOIN budget_analytic ba ON ba.id = bl.budget_analytic_id AND ba.budget_type != 'revenue'
                        WHERE po.date_order >= bl.date_from
                          AND po.date_order <= bl.date_to
                          AND po.company_id = bl.company_id
                          AND %(condition)s
                   ) AS budget ON TRUE
             WHERE pol.qty_invoiced < pol.product_qty
            """,
            analytic_fields=SQL(', ').join(self.env['account.analytic.line']._field_to_sql('a', fname) for fname in plan_fnames),
            field_cast=SQL(', ').join(SQL(f'{fname} FLOAT') for fname in plan_fnames),
            condition=SQL(' AND ').join(SQL(
                "%(bl)s IS NULL OR %(a)s = %(bl)s",
                bl=self.env['budget.line']._field_to_sql('bl', fname),
                a=self.env['budget.line']._field_to_sql('a', fname),
            ) for fname in plan_fnames)
        )

    @property
    def _table_query(self):
        project_plan, other_plans = self.env['account.analytic.plan']._get_all_plans()
        plan_fnames = [plan._column_name() for plan in project_plan | other_plans]
        return SQL(
            "%s UNION ALL %s UNION ALL %s",
            self._get_bl_query(plan_fnames),
            self._get_aal_query(plan_fnames),
            self._get_pol_query(plan_fnames),
        )

    def action_open_reference(self):
        self.ensure_one()
        if self.res_model == 'account.analytic.line':
            analytical_line = self.env['account.analytic.line'].browse(self.res_id)
            if analytical_line.move_line_id:
                return analytical_line.move_line_id.action_open_business_doc()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'form',
            'res_id': self.res_id,
        }
