import { PosData } from "@point_of_sale/app/models/data_service";
import { patch } from "@web/core/utils/patch";

patch(PosData.prototype, {
    /**
     * @override
     */
    async preLoadData(data) {
        const loadData = await super.preLoadData(data);
        if (loadData["pos.order"]) {
            loadData["pos.order"] = loadData["pos.order"].filter((o) => !o.delivery_identifier);
        }
        if (loadData["pos.order.line"]) {
            loadData["pos.order.line"] = loadData["pos.order.line"].filter((ol) => !ol.order_id);
        }
        return loadData;
    },
});
