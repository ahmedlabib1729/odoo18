# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)


class AddSixTerminal(models.TransientModel):
    _name = "pos_iot_six.add_six_terminal"
    _description = "Connect a Six Payment Terminal"

    iot_box_id = fields.Many2one(
        "iot.box",
        string="IoT Box",
        help="The IoT Box that your Six terminal is connected to.",
        required=True,
        default=lambda self: self._get_existing_iot_box_id()
    )
    iot_box_url = fields.Char(related="iot_box_id.ip_url")
    six_terminal_id = fields.Char(related="iot_box_id.six_terminal_id", readonly=False)
    terminal_device_id = fields.Many2one("iot.device", string="Terminal Device", required=True, default=lambda self: self._get_existing_terminal_device_id())

    def _get_existing_terminal_device_id(self):
        payment_method = self.env["pos.payment.method"].browse(self.env.context["active_id"])
        return payment_method.iot_device_id

    def _get_existing_iot_box_id(self):
        payment_method = self.env["pos.payment.method"].browse(self.env.context["active_id"])
        return payment_method.iot_device_id.iot_id

    @api.constrains("six_terminal_id")
    def _check_six_terminal_id(self):
        if self.six_terminal_id and not self.six_terminal_id.isdigit():
            raise ValidationError(_("Six Terminal ID must only contain digits."))

    @api.onchange("iot_box_id")
    def _on_change_iot_box_id(self):
        if self.terminal_device_id and self.terminal_device_id.iot_id != self.iot_box_id:
            self.terminal_device_id = None

    @api.onchange("six_terminal_id")
    def _on_change_six_terminal_id(self):
        if not self.iot_box_url:
            return
        self._check_six_terminal_id()
        try:
            if self.six_terminal_id:
                response = requests.post(
                    f"{self.iot_box_url}/six_payment_terminal_add",
                    data={"terminal_id": self.six_terminal_id},
                    timeout=5
                )
            else:
                response = requests.get(f"{self.iot_box_url}/six_payment_terminal_clear", timeout=5)
            response.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError, requests.ReadTimeout):
            _logger.exception("IoT Six request failed")
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _("Failed to save Six Terminal ID to IoT Box"),
                    "type": "Notification",
                }
            }

    def action_add_payment_method(self):
        self.ensure_one()
        payment_method = self.env["pos.payment.method"].browse(self.env.context["active_id"])
        payment_method.iot_device_id = self.terminal_device_id
