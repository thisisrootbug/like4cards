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
                res = super(PosOrderLine,self).create(values)
                res.state = 'paid'

class PosOrder(models.Model):
    _inherit='pos.order'

    @api.model
    def _process_order(self, pos_order):
        for line in pos_order['lines']:
            product_id = self.env['product.product'].search([("id","=",line[2]['product_id'])],limit=1)
            if not product_id:
                line[2]['product_id'] = self.env.ref("like4cards.main_product").id
        return super(PosOrder,self)._process_order(pos_order)
                

