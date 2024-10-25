# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import string

from odoo import models
from odoo.tools import populate

_logger = logging.getLogger(__name__)


class WhatsappMessage(models.Model):
    _inherit = "whatsapp.message"

    _populate_dependencies = ["whatsapp.template", "mail.message"]
    _populate_sizes = {'small': 100, 'medium': 1_500, 'large': 25_000}

    def _populate_factories(self):
        random = populate.Random("whatsapp.message")
        templates = self.env["whatsapp.template"].browse(self.env.registry.populated_models["whatsapp.template"])
        templates = templates.filtered(lambda template: template.status == 'approved')
        accounts = self.env.registry.populated_models["whatsapp.account"]
        messages = self.env.registry.populated_models["mail.message"]
        message_type = ['outbound', 'inbound']
        state = ['outgoing', 'sent', 'delivered', 'read', 'received', 'error', 'cancel']

        def compute_mobile_number(**kwargs):
            return ''.join(random.choices(string.digits[1:], k=10))

        def generate_random_message_uid(**kwargs):
            return ''.join(random.choices(string.ascii_uppercase, k=10))

        def compute_wa_template_id(**kwargs):
            return random.choice(templates.ids)

        return [
            ('mobile_number', populate.compute(compute_mobile_number)),
            ('message_type', populate.randomize(message_type)),
            ('state', populate.randomize(state)),
            ('wa_template_id', populate.compute(compute_wa_template_id)),
            ('msg_uid', populate.compute(generate_random_message_uid)),
            ('wa_account_id', populate.randomize(accounts)),
            ('mail_message_id', populate.randomize(messages)),
        ]
