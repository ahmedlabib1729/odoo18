# Part of Odoo. See LICENSE file for full copyright and licensing details.

import string

from odoo import models
from odoo.tools import populate


class WhatsappAccount(models.Model):
    _inherit = "whatsapp.account"

    _populate_dependencies = ["res.users"]
    _populate_sizes = {'small': 2, 'medium': 5, 'large': 10}

    def _populate_factories(self):
        random = populate.Random("whatsapp.account")
        users = self.env.registry.populated_models["res.users"]

        def generate_random_app_id_secret(**kwargs):
            return ''.join(random.choices(string.ascii_uppercase, k=15))

        def generate_random_account_uid(**kwargs):
            return ''.join(random.choices(string.ascii_uppercase, k=10))

        def generate_random_phone_uid(**kwargs):
            return ''.join(random.choices(string.digits[1:], k=10))

        def generate_random_access_token(**kwargs):
            return ''.join(random.choices(string.ascii_uppercase, k=20))

        def get_notify_user_ids(**kwargs):
            return [
                (6, 0, [
                    random.choice(users) for i in range(random.randint(1, len(users)))
                ])
            ]
        return [
            ('name', populate.constant("WA-ac-{counter}")),
            ('app_uid', populate.compute(generate_random_app_id_secret)),
            ('app_secret', populate.compute(generate_random_app_id_secret)),
            ('account_uid', populate.compute(generate_random_account_uid)),
            ('phone_uid', populate.compute(generate_random_phone_uid)),
            ('token', populate.compute(generate_random_access_token)),
            ('notify_user_ids', populate.compute(get_notify_user_ids)),
        ]
