from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_fields_stock_barcode(self):
        return super()._get_fields_stock_barcode() + ['product_uom']
