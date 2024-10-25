# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models
from odoo.tools import populate

_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = "mail.message"

    def _populate(self, size):
        res = super()._populate(size)
        random = populate.Random("mail.message in WhatsApp")
        channels = self.env["discuss.channel"].browse(self.env.registry.populated_models["discuss.channel"])
        messages = []
        big_done = 0
        for channel in channels.filtered(lambda channel: channel.channel_type == "whatsapp"):
            big = {"small": 80, "medium": 150, "large": 300}[size]
            small_big_ratio = {"small": 10, "medium": 150, "large": 1000}[size]
            max_messages = big if random.randint(1, small_big_ratio) == 1 else 60
            number_messages = 200 if big_done < 2 else random.randrange(max_messages)
            if number_messages >= 200:
                big_done += 1
            for counter in range(number_messages):
                messages.append(
                    {
                        "author_id": random.choice(channel.channel_member_ids.partner_id).id,
                        "body": f"whatsapp_message_body_{counter}",
                        "message_type": "whatsapp_message",
                        "model": "discuss.channel",
                        "res_id": channel.id,
                    }
                )
        batches = [messages[i : i + 1000] for i in range(0, len(messages), 1000)]
        count = 0
        for batch in batches:
            count += len(batch)
            _logger.info("Batch of mail.message for discuss.channel(whatsapp): %s/%s", count, len(messages))
            res += self.env["mail.message"].create(batch)
        return res
