/** @odoo-module */

import { CommonOdooChartConfigPanel } from "../common/config_panel";
import { _t } from "@web/core/l10n/translation";
import { components } from "@odoo/o-spreadsheet";

const { Checkbox } = components;

export class OdooLineChartConfigPanel extends CommonOdooChartConfigPanel {
    static template = "spreadsheet_edition.OdooLineChartConfigPanel";
    static components = {
        ...CommonOdooChartConfigPanel.components,
        Checkbox,
    };

    get stackedLabel() {
        return _t("Stacked linechart");
    }

    get cumulativeLabel() {
        return _t("Cumulative data");
    }

    onUpdateStacked(stacked) {
        this.props.updateChart(this.props.figureId, {
            stacked,
        });
    }
    onUpdateCumulative(cumulative) {
        this.props.updateChart(this.props.figureId, {
            cumulative,
        });
    }
}
