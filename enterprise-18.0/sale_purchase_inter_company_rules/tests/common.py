# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.account_inter_company_rules.tests.common import TestInterCompanyRulesCommon


class TestInterCompanyRulesCommonSOPO(TestInterCompanyRulesCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.res_users_company_a.groups_id += cls.env.ref('sales_team.group_sale_salesman') + cls.env.ref('purchase.group_purchase_user')
        cls.res_users_company_b.groups_id += cls.env.ref('sales_team.group_sale_salesman') + cls.env.ref('purchase.group_purchase_user')
