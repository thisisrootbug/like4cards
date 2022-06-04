from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    note = fields.Char()

    @api.model
    def create(self, values):
        if values.get('product_id'):
            product_id = self.env['product.product'].search([("id","=",values.get("product_id"))],limit=1)
            if product_id:
                return super(PosOrderLine,self).create(values)
            else:
                product_id = self.env.ref("like4cards.main_product")
                values["product_id"] = product_id.id
                _logger.info(values)
                res = super(PosOrderLine,self).create(values)
                _logger.info(res)
                

