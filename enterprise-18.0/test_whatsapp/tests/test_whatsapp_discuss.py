# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.addons.whatsapp.tests.common import MockIncomingWhatsApp
from odoo.addons.test_whatsapp.tests.common import WhatsAppFullCase


class WhatsAppMessageDiscuss(WhatsAppFullCase, MockIncomingWhatsApp):
    def test_message_reaction(self):
        """Check a reaction is correctly added on a whatsapp message."""
        with self.mockWhatsappGateway():
            self._receive_whatsapp_message(self.whatsapp_account, "test", "32499123456")
        discuss_channel = self.assertWhatsAppDiscussChannel(
            "32499123456",
            wa_msg_count=1,
            msg_count=1,
        )
        message = discuss_channel.message_ids[0]
        with self.mockWhatsappGateway():
            self._receive_whatsapp_message(
                self.whatsapp_account,
                "",
                "32499123456",
                additional_message_values={
                    "reaction": {
                        "message_id": message.wa_message_ids[0].msg_uid,
                        "emoji": "😊",
                    },
                    "type": "reaction",
                },
            )
        self._reset_bus()
        with self.assertBus(
            [
                (self.cr.dbname, "discuss.channel", discuss_channel.id),
                (self.cr.dbname, "discuss.channel", discuss_channel.id),
            ],
            [
                {
                    "type": "mail.record/insert",
                    "payload": {
                        "mail.message": [
                            {
                                "id": message.id,
                                "reactions": [["DELETE", {"message": message.id, "content": "😊"}]],
                            }
                        ]
                    },
                },
                {
                    "type": "mail.record/insert",
                    "payload": {
                        "MessageReactions": [
                            {
                                "content": "👍",
                                "count": 1,
                                "message": message.id,
                                "personas": [{"id": message.author_id.id, "type": "partner"}],
                                # new reaction, and there is no way that we can get the id of the reaction, so that the sequence is directly +1
                                "sequence": message.reaction_ids.ids[0] + 1,
                            }
                        ],
                        "mail.message": [
                            {
                                "id": message.id,
                                "reactions": [["ADD", [{"message": message.id, "content": "👍"}]]],
                            }
                        ],
                        "res.partner": [
                            {
                                "id": message.author_id.id,
                                "name": "+32499123456",
                                "write_date": fields.Datetime.to_string(
                                    message.author_id.write_date
                                ),
                            }
                        ],
                    },
                },
            ],
        ):
            with self.mockWhatsappGateway():
                self._receive_whatsapp_message(
                    self.whatsapp_account,
                    "",
                    "32499123456",
                    additional_message_values={
                        "reaction": {
                            "message_id": message.wa_message_ids[0].msg_uid,
                            "emoji": "👍",
                        },
                        "type": "reaction",
                    },
                )
