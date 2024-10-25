# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestTags(TransactionCase):

    def test_create_tag(self):
        tag = self.env['documents.tag'].create({'name': 'Foo'})
        self.assertTrue(tag.sequence > 0, 'should have a non-zero sequence')
