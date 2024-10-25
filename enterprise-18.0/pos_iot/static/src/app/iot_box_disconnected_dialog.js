import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class iotBoxDisconnectedDialog extends Component {
    static components = { Dialog };
    static props = {
        url: String,
    };
    static template = "pos_iot.IotBoxDisconnectedDialog";
}
