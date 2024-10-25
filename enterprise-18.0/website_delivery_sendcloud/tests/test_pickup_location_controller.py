# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests
import json

from unittest.mock import patch
from contextlib import contextmanager
from odoo.addons.website_sale.controllers.delivery import Delivery
from odoo.addons.website.tools import MockRequest
from odoo.tests import TransactionCase, tagged


@contextmanager
def _mock_call():
    def _mock_request(*args, **kwargs):
        method = kwargs.get('method') or args[0]
        url = kwargs.get('url') or args[1]
        responses = {
            'get': {
                'service-points': [{
                    'id': 11238037,
                    'name': 'STATION AVIA',
                    'formatted_opening_times': {
                        '0': ['07:00 - 18:30'],
                        '1': ['07:00 - 18:30'],
                        '2': ['07:00 - 18:30'],
                        '3': ['07:00 - 18:30'],
                        '4': ['08:00 - 14:00', '15:00 - 18:00'],
                        '5': ['09:00 - 16:00'],
                        '6': [],
                    },
                    'street': 'CHAUSSEE DE NAMUR',
                    'house_number': '67',
                    'city': 'RAMILLIES',
                    'postal_code': '1367',
                    'country': 'BE',
                    'latitude': '50.634529',
                    'longitude': '4.864696',
                }],
            },
            'post': {
            }
        }

        for endpoint, content in responses[method].items():
            if endpoint in url:
                response = requests.Response()
                response._content = json.dumps(content).encode()
                response.status_code = 200
                return response

        raise Exception('unhandled request url %s' % url)

    with patch.object(requests.Session, 'request', _mock_request):
        yield


@tagged('post_install', '-at_install')
class TestWebsiteDeliverySendcloudLocationsController(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.your_company = cls.env.ref("base.main_partner")
        cls.warehouse_id = cls.env['stock.warehouse'].search([('company_id', '=', cls.your_company.id)], limit=1)
        cls.your_company.write({'name': 'Odoo SA',
                                'country_id': cls.env.ref('base.be').id,
                                'street': 'Chaussée de Namur 40',
                                'street2': False,
                                'state_id': False,
                                'city': 'Ramillies',
                                'zip': 1367,
                                'phone': '081813700',
                                })
        # partner will be in europe
        cls.eu_partner = cls.env['res.partner'].create({
            'name': 'newPartner',
            'country_id': cls.env.ref('base.be').id,
            'zip': '1367',
            'state_id': False,
            'country_code': 'BE',
            'street': 'Rue des Bourlottes 9',
            'city': 'Ramillies'
        })

        cls.product_to_ship1 = cls.env["product.product"].create({
            'name': 'Door with wings',
            'type': 'consu',
            'weight': 10.0
        })

        shipping_product = cls.env['product.product'].create({
            'name': 'SendCloud Delivery',
            'type': 'service'
        })

        uom = cls.env.ref('uom.product_uom_meter')

        # Allow customization of 'sendcloud_use_locations' on the delivery_carrier
        cls.sendcloud_shipping = cls.env['sendcloud.shipping.product'].create({
                'name': 'Test product',
                'sendcloud_code': 'test',
                'carrier': 'Test',
                'min_weight': 1,
                'max_weight': 50001,
                'functionalities': {
                    'bool_func': [],
                    'detail_func': {},
                    'customizable': {
                        'last_mile': [
                            'service_point',
                            'home_delivery',
                        ]
                    },
                },
        })

        cls.sendcloud = cls.env['delivery.carrier'].create({
            'delivery_type': 'sendcloud',
            'product_id': shipping_product.id,
            'sendcloud_public_key': 'mock_key',
            'sendcloud_secret_key': 'mock_key',
            'name': 'SendCloud',
            'sendcloud_locations_radius_value': 1000,
            'sendcloud_locations_radius_unit': uom.id,
            'sendcloud_locations_id': 1,
            'sendcloud_shipping_id': cls.sendcloud_shipping.id,
        })

        cls.sendcloud.sendcloud_use_locations = True
        cls.payment_provider = cls.env['payment.provider'].create({'name': 'test'})

        cls.payment_method_id = cls.env.ref('payment.payment_method_unknown').id

        cls.partner = cls.env['res.partner'].create({'name': 'testestset'})

        cls.currency = cls.env['res.currency'].create({'name': 'testestset', 'symbol': '€'})

        cls.transaction = cls.env['payment.transaction'].create({
            'state': 'draft',
            'provider_id': cls.payment_provider.id,
            'payment_method_id': cls.payment_method_id,
            'partner_id': cls.partner.id,
            'currency_id': cls.currency.id,
            'amount': 42
        })

        cls.order = cls.env['sale.order'].create({
            'carrier_id': cls.sendcloud.id,
            'partner_id': cls.env.user.partner_id.id,
            'partner_shipping_id': cls.eu_partner.id,
            'transaction_ids': [cls.transaction.id]
        })

    def test_controller_pickup_location(self):
        with MockRequest(self.env, website=self.website, sale_order_id=self.order.id):
            with _mock_call():
                response = Delivery().website_sale_get_pickup_locations()
                self.assertNotEqual({},
                    Delivery().website_sale_set_pickup_location(
                        pickup_location_data=json.dumps(response['pickup_locations'][0])
                    )
                )
                self.assertEqual({
                    'id': 11238037,
                    'name': 'Station Avia',
                    'opening_hours': {
                        '0': ['07:00 - 18:30'],
                        '1': ['07:00 - 18:30'],
                        '2': ['07:00 - 18:30'],
                        '3': ['07:00 - 18:30'],
                        '4': ['08:00 - 14:00', '15:00 - 18:00'],
                        '5': ['09:00 - 16:00'],
                        '6': [],
                    },
                    'street': 'Chaussee De Namur 67',
                    'city': 'Ramillies',
                    'zip_code': '1367',
                    'country_code': 'BE',
                    'latitude': '50.634529',
                    'longitude': '4.864696',
                }, self.order.pickup_location_data)
