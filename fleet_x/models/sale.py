# -*- coding: utf-8 -*-

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vehicle_id = fields.Many2one("fleet.vehicle", u"Vehículo")