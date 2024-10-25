# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import Command
from odoo.tests import Form
from odoo.tests.common import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestShopFloor(HttpCase):

    def setUp(self):
        super().setUp()
        # Set Administrator as the current user.
        self.uid = self.env.ref('base.user_admin').id
        # Enables Work Order setting, and disables other settings.
        group_workorder = self.env.ref('mrp.group_mrp_routings')
        self.env.user.write({'groups_id': [(4, group_workorder.id, 0)]})

        group_lot = self.env.ref('stock.group_production_lot')
        group_multi_loc = self.env.ref('stock.group_stock_multi_locations')
        group_pack = self.env.ref('stock.group_tracking_lot')
        group_uom = self.env.ref('uom.group_uom')
        self.env.user.write({'groups_id': [(3, group_lot.id)]})
        self.env.user.write({'groups_id': [(3, group_multi_loc.id)]})
        self.env.user.write({'groups_id': [(3, group_pack.id)]})
        # Explicitly remove the UoM group.
        group_user = self.env.ref('base.group_user')
        group_user.write({'implied_ids': [(3, group_uom.id)]})
        self.env.user.write({'groups_id': [(3, group_uom.id)]})

    def test_shop_floor(self):
        # Creates somme employees for test purpose.
        self.env['hr.employee'].create([{
            'name': name,
            'company_id': self.env.company.id,
        } for name in ['Abbie Seedy', 'Billy Demo', 'Cory Corrinson']])

        giraffe = self.env['product.product'].create({
            'name': 'Giraffe',
            'is_storable': True,
            'tracking': 'lot',
        })
        leg = self.env['product.product'].create({
            'name': 'Leg',
            'is_storable': True,
        })
        neck = self.env['product.product'].create({
            'name': 'Neck',
            'is_storable': True,
            'tracking': 'serial',
        })
        color = self.env['product.product'].create({
            'name': 'Color',
            'is_storable': True,
        })
        neck_sn_1, neck_sn_2 = self.env['stock.lot'].create([{
            'name': 'NE1',
            'product_id': neck.id,
        }, {
            'name': 'NE2',
            'product_id': neck.id,
        }])
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        stock_location = warehouse.lot_stock_id
        self.env['stock.quant']._update_available_quantity(leg, stock_location, quantity=100)
        self.env['stock.quant']._update_available_quantity(color, stock_location, quantity=100)
        self.env['stock.quant']._update_available_quantity(neck, stock_location, quantity=1, lot_id=neck_sn_1)
        self.env['stock.quant']._update_available_quantity(neck, stock_location, quantity=1, lot_id=neck_sn_2)
        savannah = self.env['mrp.workcenter'].create({
            'name': 'Savannah',
            'time_start': 10,
            'time_stop': 5,
            'time_efficiency': 80,
        })
        jungle = self.env['mrp.workcenter'].create({'name': 'Jungle'})
        picking_type = warehouse.manu_type_id
        bom = self.env['mrp.bom'].create({
            'product_id': giraffe.id,
            'product_tmpl_id': giraffe.product_tmpl_id.id,
            'product_uom_id': giraffe.uom_id.id,
            'product_qty': 1.0,
            'consumption': 'flexible',
            'operation_ids': [
                (0, 0, {
                'name': 'Creation',
                'workcenter_id': savannah.id,
            }), (0, 0, {
                'name': 'Release',
                'workcenter_id': jungle.id,
            })],
            'bom_line_ids': [
                (0, 0, {'product_id': leg.id, 'product_qty': 4}),
                (0, 0, {'product_id': neck.id, 'product_qty': 1, 'manual_consumption': True})
            ]
        })
        steps_common_values = {
            'picking_type_ids': [(4, picking_type.id)],
            'product_ids': [(4, giraffe.id)],
            'operation_id': bom.operation_ids[0].id,
        }
        self.env['quality.point'].create([
            {
                **steps_common_values,
                'title': 'Register Production',
                'test_type_id': self.env.ref('mrp_workorder.test_type_register_production').id,
                'sequence': 0,
            },
            {
                **steps_common_values,
                'title': 'Instructions',
                'test_type_id': self.env.ref('quality.test_type_instructions').id,
                'sequence': 1,
            },
            {
                **steps_common_values,
                'title': 'Register legs',
                'component_id': leg.id,
                'test_type_id': self.env.ref('mrp_workorder.test_type_register_consumed_materials').id,
                'sequence': 2,
            },
            {
                **steps_common_values,
                'title': 'Register necks',
                'component_id': neck.id,
                'test_type_id': self.env.ref('mrp_workorder.test_type_register_consumed_materials').id,
                'sequence': 3,
            },
            {
                **steps_common_values,
                'title': 'Release',
                'test_type_id': self.env.ref('quality.test_type_instructions').id,
                'sequence': 4,
            },
        ])
        mo = self.env['mrp.production'].create({
            'product_id': giraffe.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()

        # Tour
        action = self.env["ir.actions.actions"]._for_xml_id("mrp_workorder.action_mrp_display")
        url = f"/odoo/action-{action['id']}"
        self.start_tour(url, "test_shop_floor", login='admin')

        self.assertEqual(mo.move_finished_ids.quantity, 2)
        self.assertRecordValues(mo.move_raw_ids, [
            {'product_id': leg.id, 'quantity': 10.0, 'state': 'done'},
            {'product_id': neck.id, 'quantity': 2.0, 'state': 'done'},
            {'product_id': color.id, 'quantity': 1.0, 'state': 'done'},
        ])
        self.assertRecordValues(mo.workorder_ids, [
            {'state': 'done', 'workcenter_id': savannah.id},
            {'state': 'done', 'workcenter_id': jungle.id},
        ])
        self.assertRecordValues(mo.workorder_ids[0].check_ids, [
            {'quality_state': 'pass', 'component_id': False, 'qty_done': 2, 'lot_id': mo.move_finished_ids.move_line_ids.lot_id.id},
            {'quality_state': 'pass', 'component_id': False, 'qty_done': 0, 'lot_id': 0},
            {'quality_state': 'pass', 'component_id': leg.id, 'qty_done': 8, 'lot_id': 0},
            {'quality_state': 'pass', 'component_id': leg.id, 'qty_done': 2, 'lot_id': 0},
            {'quality_state': 'pass', 'component_id': neck.id, 'qty_done': 1, 'lot_id': neck_sn_2.id},
            {'quality_state': 'pass', 'component_id': neck.id, 'qty_done': 1, 'lot_id': neck_sn_1.id},
            {'quality_state': 'pass', 'component_id': False, 'qty_done': 0, 'lot_id': 0},
        ])

    def test_generate_serials_in_shopfloor(self):
        component1 = self.env['product.product'].create({
            'name': 'comp1',
            'is_storable': True,
        })
        component2 = self.env['product.product'].create({
            'name': 'comp2',
            'is_storable': True,
        })
        finished = self.env['product.product'].create({
            'name': 'finish',
            'is_storable': True,
        })
        byproduct = self.env['product.product'].create({
            'name': 'byprod',
            'is_storable': True,
            'tracking': 'serial',
        })
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        stock_location = warehouse.lot_stock_id
        self.env['stock.quant']._update_available_quantity(component1, stock_location, quantity=100)
        self.env['stock.quant']._update_available_quantity(component2, stock_location, quantity=100)
        workcenter = self.env['mrp.workcenter'].create({
            'name': 'Assembly Line',
        })
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': finished.product_tmpl_id.id,
            'product_qty': 1.0,
            'operation_ids': [
                (0, 0, {'name': 'Assemble', 'workcenter_id': workcenter.id}),
            ],
            'bom_line_ids': [
                (0, 0, {'product_id': component1.id, 'product_qty': 1}),
                (0, 0, {'product_id': component2.id, 'product_qty': 1}),
            ],
            'byproduct_ids': [
                (0, 0, {'product_id': byproduct.id, 'product_qty': 1}),
            ]
        })
        bom.byproduct_ids[0].operation_id = bom.operation_ids[0].id
        mo = self.env['mrp.production'].create({
            'product_id': finished.id,
            'product_qty': 1,
            'bom_id': bom.id,
        })
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()

        action = self.env["ir.actions.actions"]._for_xml_id("mrp_workorder.action_mrp_display")
        url = f"/odoo/action-{action['id']}"
        self.start_tour(url, "test_generate_serials_in_shopfloor", login='admin')

    def test_canceled_wo(self):
        finished = self.env['product.product'].create({
            'name': 'finish',
            'is_storable': True,
        })
        workcenter = self.env['mrp.workcenter'].create({
            'name': 'Assembly Line',
        })
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': finished.product_tmpl_id.id,
            'product_qty': 1.0,
            'operation_ids': [
                (0, 0, {'name': 'op1', 'workcenter_id': workcenter.id}),
                (0, 0, {'name': 'op2', 'workcenter_id': workcenter.id}),
            ],
        })

        # Cancel previous MOs and create a new one
        self.env['mrp.production'].search([]).action_cancel()
        mo = self.env['mrp.production'].create({
            'product_id': finished.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        mo.action_confirm()
        mo.action_assign()
        mo.button_plan()

        # wo_1 completely finished
        mo_form = Form(mo)
        mo_form.qty_producing = 2
        mo = mo_form.save()
        mo.workorder_ids[0].button_start()
        mo.workorder_ids[0].button_finish()

        # wo_2 partially finished
        mo_form.qty_producing = 1
        mo = mo_form.save()
        mo.workorder_ids[1].button_start()
        mo.workorder_ids[1].button_finish()

        # Create a backorder
        action = mo.button_mark_done()
        backorder = Form(self.env['mrp.production.backorder'].with_context(**action['context']))
        backorder.save().action_backorder()
        mo_backorder = mo.procurement_group_id.mrp_production_ids[-1]
        mo_backorder.button_plan()

        # Sanity check
        self.assertEqual(mo_backorder.workorder_ids[0].state, 'cancel')
        self.assertEqual(mo_backorder.workorder_ids[1].state, 'ready')

        action = self.env["ir.actions.actions"]._for_xml_id("mrp_workorder.action_mrp_display")
        url = f"/odoo/action-{action['id']}"
        self.start_tour(url, "test_canceled_wo", login='admin')

    def test_change_qty_produced(self):
        """
            Check that component quantity matches the quantity produced set in the shop
            floor register production change to the quantity produced
            Example:
                move.uom_unit = 2.
                bom.final_quantity = 1
                MO.qty_producing = 5 -> should consume 10 components for move_raw.
                Confirm MO and update MO.qty_producing = 3
                Finish the workorder, then it should consume 6 components for move_raw.
            The above behaviour should be occur on the MO form and shop floor.
        """
        demo = self.env['product.product'].create({
            'name': 'DEMO'
        })
        comp1 = self.env['product.product'].create({
            'name': 'COMP1',
            'is_storable': True
        })
        comp2 = self.env['product.product'].create({
            'name': 'COMP2',
            'is_storable': True
        })
        work_center = self.env['mrp.workcenter'].create({"name": "WorkCenter", "time_start": 11})
        uom_unit = self.env.ref('uom.product_uom_unit')
        bom = self.env['mrp.bom'].create({
            'product_id': demo.id,
            'product_tmpl_id': demo.product_tmpl_id.id,
            'product_uom_id': uom_unit.id,
            'product_qty': 1.0,
            'type': 'normal',
            'operation_ids': [
                Command.create({'name': 'OP1', 'workcenter_id': work_center.id, 'time_cycle': 12, 'sequence': 1}),
                Command.create({'name': 'OP2', 'workcenter_id': work_center.id, 'time_cycle': 18, 'sequence': 2})
            ]
        })
        self.env['mrp.bom.line'].create([
            {
                'product_id': comp.id,
                'product_qty': qty,
                'bom_id': bom.id,
                'operation_id': operation.id,
            } for comp, qty, operation in zip([comp1, comp2], [1.0, 2.0], bom.operation_ids)
        ])
        self.env['stock.quant'].create([
            {
                'location_id': self.env.ref('stock.warehouse0').lot_stock_id.id,
                'product_id': comp.id,
                'inventory_quantity': 20,
            } for comp in [comp1, comp2]
        ]).action_apply_inventory()

        mo_form = Form(self.env['mrp.production'])
        mo_form.bom_id = bom
        mo_form.product_qty = 5
        mo = mo_form.save()
        mo.action_confirm()

        wo = mo.workorder_ids.sorted()[0]
        wo.button_start()
        wo.button_finish()

        self.start_tour("/odoo/shop-floor", "test_change_qty_produced", login='admin')
        self.assertEqual(mo.qty_producing, 3)
        for move in mo.move_raw_ids:
            if move.product_id.id == comp1.id:
                self.assertEqual(move.quantity, 5)
                self.assertTrue(move.picked)
            if move.product_id.id == comp2.id:
                self.assertEqual(move.quantity, 6)
                self.assertTrue(move.picked)
