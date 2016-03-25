# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    vehicle_model = fields.Many2one("fleet.vehicle.model", "Modelo")
    is_vehicle = fields.Boolean(u"Es un vehículo")

    @api.onchange("is_vehicle")
    def onchange_is_vehicle(self):
        if self.is_vehicle:
            self.type = "product"
            self.tracking = "serial"
        else:
            self.type = "service"
            self.tracking = "none"

    @api.onchange("vehicle_model")
    def onchange_vehicle_model(self):
        if self.vehicle_model:
            self.name = "{}/{}".format(self.vehicle_model.brand_id.name,self.vehicle_model.name)


class StockProdcutLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        if vals.get("product_id", False):
            product = self.env["product.template"].browse(vals["product_id"])
            if product.is_vehicle:
                res = self.env["fleet.vehicle"].create({"model_id": product.vehicle_model.id, "vin_sn": vals.get("name", "Pendiente de digitar")})
                print res
        return super(StockProdcutLot, self).create(vals)
