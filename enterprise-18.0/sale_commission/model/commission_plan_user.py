# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import models, fields, exceptions, _, api


class CommissionPlanUser(models.Model):
    _name = 'sale.commission.plan.user'
    _description = 'Commission Plan User'
    _order = 'id'

    plan_id = fields.Many2one('sale.commission.plan', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', "Salesperson", required=True, domain="[('share', '=', False)]")

    date_from = fields.Date("From", compute='_compute_date_from', store=True, readonly=False)
    date_to = fields.Date("To")

    other_plans = fields.Many2many('sale.commission.plan', string="Other plans", compute='_compute_other_plans', readonly=False)

    _sql_constraints = [
        ('user_uniq', 'unique (plan_id, user_id)', "The user is already present in the plan"),
    ]

    @api.constrains('date_from', 'date_to')
    def _date_constraint(self):
        for user in self:
            if user.date_to and user.date_to < user.date_from:
                raise exceptions.UserError(_("From must be before To"))
            if user.date_from < user.plan_id.date_from:
                raise exceptions.UserError(_("User period cannot start before the plan."))
            if user.date_to and user.date_to > user.plan_id.date_to:
                raise exceptions.UserError(_("User period cannot end after the plan."))

    @api.depends('user_id')
    def _compute_other_plans(self):
        grouped_users = defaultdict(lambda: self.env['sale.commission.plan.user'])
        for user in self | self.search([('user_id', 'in', self.user_id.ids), ('plan_id.state', 'in', ['draft', 'approved'])]):
            grouped_users[user.user_id] += user

        for plan_users in grouped_users.values():
            for plan_user in plan_users:
                plan_user.other_plans = plan_users.plan_id - plan_user.plan_id

    @api.depends('plan_id')
    def _compute_date_from(self):
        today = fields.Date.today()
        for user in self:
            if user.date_from:
                return
            if not user.plan_id.date_from:
                return
            user.date_from = max(user.plan_id.date_from, today) if user.plan_id.state != 'draft' else user.plan_id.date_from
