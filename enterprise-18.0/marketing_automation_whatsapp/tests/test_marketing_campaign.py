# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.whatsapp.tests.common import WhatsAppCommon, MockIncomingWhatsApp


class MarketingCampaign(WhatsAppCommon, MockIncomingWhatsApp):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.phone = '+32499123456'
        cls.template = cls.env['whatsapp.template'].create({
            'body': 'Hello {{1}}',
            'name': 'Test-dynamic',
            'status': 'approved',
            'wa_account_id': cls.whatsapp_account.id,
            "button_ids": [
                        (0, 0, {
                            'sequence': 0,
                            "button_type": "url",
                            "name": "tracked url",
                            "url_type": 'tracked',
                            "website_url": "https://www.tracked.com",
                        }),
                        (0, 0, {
                            'sequence': 1,
                            "button_type": "url",
                            "name": "dynamic url",
                            "url_type": 'dynamic',
                            "website_url": "https://www.dynamic.com",
                        })
                ]
        })

        cls.whatsapp_test_customer = cls.env['res.partner'].create({
            'name': 'Wa Test Marketing Automation',
            'mobile': cls.phone
        })

        cls.campaign = cls.env['marketing.campaign'].create({
            'domain': [('mobile', '=', cls.phone), ('name', '=', 'Wa Test Marketing Automation')],
            'model_id': cls.env['ir.model']._get_id('res.partner'),
            'name': 'Test Campaign',
        })

    def test_detect_responses(self):
        """ Test reply mechanism on whatsapp """
        vals = {
            'name': 'Test Activity',
            'activity_type': 'whatsapp',
            'whatsapp_template_id': self.template.id,
            'campaign_id': self.campaign.id,
            'model_id': self.env['ir.model']._get_id('res.partner')
        }
        activity = self.env['marketing.activity'].create(vals)
        self.campaign.sync_participants()

        # sent message
        with self.mockWhatsappGateway():
            self.campaign.execute_activities()

        traces = self.env['marketing.trace'].search([
            ('activity_id', 'in', activity.ids),
        ])
        # recieve message
        with self.mockWhatsappGateway():
            self._receive_whatsapp_message(
                self.whatsapp_account, "Hello, it's reply", self.phone,
            )
        self.assertEqual(traces.whatsapp_message_id.state, 'replied')

    def test_get_template_button_component_tracking(self):
        button_component = self.template._get_template_button_component()
        button1_url = button_component['buttons'][0]['url']
        button1_example = button_component['buttons'][0]['example']
        host_url = self.env['link.tracker'].get_base_url().strip('/')

        self.assertEqual(button1_url, host_url + '/{{1}}')
        self.assertEqual(button1_example, host_url + '/???')
