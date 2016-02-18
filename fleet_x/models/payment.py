# -*- coding: utf-8 -*-

from openerp import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    vehicle_id = fields.Many2one("fleet.vehicle", u"Vehículo")
