# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.tests import Form


class TestQualityCheck(TransactionCase):

    def test_change_quality_point(self):
        """
        Test that a quality point can be used with an incompatible product.
        """
        product_a = self.env['product.product'].create({
            'name': 'product a',
        })
        product_b = self.env['product.product'].create({
            'name': 'product b',
        })
        qp_product_a = self.env['quality.point'].create({
            'product_ids': [(4, product_a.id)],
        })
        qp_product_b = self.env['quality.point'].create({
            'product_ids': [(4, product_b.id)],
        })
        qc = self.env['quality.check'].create({
                'product_id': product_b.id,
                'point_id': qp_product_b.id,
                'team_id': 1
            })
        qc_form = Form(qc)
        qc_form.point_id = qp_product_a
        qc = qc_form.save()
        self.assertEqual(qc.product_id, product_b)
        self.assertEqual(qc.point_id, qp_product_a)
