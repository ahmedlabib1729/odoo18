# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('grid', "Grid")])

    def _get_view_info(self):
        return {'grid': {'icon': 'fa fa-th'}} | super()._get_view_info()
