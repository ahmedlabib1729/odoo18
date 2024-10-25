# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.tools import populate
from odoo.addons.whatsapp.tools.lang_list import Languages


class WhatsappTemplate(models.Model):
    _inherit = "whatsapp.template"

    _populate_dependencies = ["whatsapp.account"]
    _populate_sizes = {'small': 10, 'medium': 100, 'large': 1000}

    def _populate_factories(self):
        random = populate.Random("whatsapp.template")
        accounts = self.env["whatsapp.account"].browse(self.env.registry.populated_models["whatsapp.account"])
        template_type = ['authentication', 'marketing', 'utility']
        header_type = ['none', 'text']
        status = [
            'approved', 'draft', 'pending', 'in_appeal', 'paused',
            'disabled', 'rejected', 'pending_deletion', 'deleted', 'limit_exceeded'
        ]
        body = [
            "Welcome to Odoo!\nWe're excited to have you.\nLet's achieve great things together.",
            "Greetings from Odoo!\nYour journey with us starts now.\nLet's make it memorable.",
            "Hello and welcome to Odoo!\nWe're here to support you.\nTogether, we'll reach new heights.",
            "Odoo welcomes you!\nJoin our community of innovators.\nLet's create something amazing.",
            "Glad to see you at Odoo!\nYour success is our priority.\nLet's work together for greatness.",
            "Welcome aboard Odoo!\nWe're thrilled to have you here.\nLet's embark on this journey together.",
            "Odoo is happy to have you!\nWe believe in your potential.\nLet's unlock it together.",
            "A warm welcome to Odoo!\nYou are now part of our family.\nLet's grow and succeed together.",
            "You are welcome at Odoo!\nWe value your presence.\nLet's achieve excellence together.",
            "Odoo greets you warmly!\nWe look forward to working with you.\nLet's make great things happen."
        ]

        def compute_lang_code(**kwargs):
            return Languages[random.randint(0, len(Languages) - 1)][0]

        def compute_wa_account_id(**kwargs):
            return random.choice(accounts.ids)

        return [
            ('name', populate.constant("WA-T-{counter}")),
            ('template_name', populate.constant("Template-{counter}")),
            ('lang_code', populate.compute(compute_lang_code)),
            ('template_type', populate.randomize(template_type)),
            ('wa_account_id', populate.compute(compute_wa_account_id)),
            ('header_type', populate.randomize(header_type)),
            ('footer_text', populate.constant("Write 'stop' to stop receiving messages")),
            ('header_text', populate.constant("Welcome to Odoo!")),
            ('status', populate.randomize(status, [55, 5, 5, 5, 5, 5, 5, 5, 5, 5])),
            ('body', populate.iterate(body)),
        ]
