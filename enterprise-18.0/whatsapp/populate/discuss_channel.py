# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import random
import string

from odoo import models

_logger = logging.getLogger(__name__)


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    @property
    def _populate_dependencies(self):
        return super()._populate_dependencies + ["whatsapp.account"]

    def _populate(self, size):
        res = super()._populate(size)
        accounts = self.env["whatsapp.account"].browse(self.env.registry.populated_models["whatsapp.account"])
        group = self.env.ref("base.group_system")
        partners = self.env["res.partner"].browse(self.env.registry.populated_models["res.partner"])
        partners = partners.filtered(lambda partner: not partner.is_company)

        def generate_random_phone(**kwargs):
            return '+91' + ''.join(random.choices(string.digits[1:], k=10))

        channels = []
        for _ in range(0, {"small": 30, "medium": 200, "large": 1000}[size]):
            whatsapp_number = generate_random_phone()
            partner = random.choice(partners)
            channels.append(
                {
                    "channel_partner_ids": [(4, partner.id)],
                    "channel_type": "whatsapp",
                    "group_ids": group,
                    "name": f"{whatsapp_number} {partner.name}",
                    'wa_account_id': random.choice(accounts.ids),
                    'whatsapp_number': whatsapp_number,
                    "whatsapp_partner_id": partner.id,
                }
            )
        # install_mode to prevent from automatically adding system as member
        res += self.env["discuss.channel"].with_context(install_mode=True).create(channels)
        return res
