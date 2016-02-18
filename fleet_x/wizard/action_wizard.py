# -*- coding: utf-8 -*-

from openerp import models, fields, api


class NewModule(models.TransientModel):
    _name = 'car.action.wizard'

    partner_id = fields.Many2one("res.partner", string="Cliente", required=True)
    action_type = fields.Selection([('quotation', u'Cotización'), ('receipt', 'Recibo')], default="quotation",
                                   string="Acciones")
    journal_id = fields.Many2one("account.journal", string="Forma de pago", domain="[('type','in',('cash','bank'))]")
    amount = fields.Float(string="Monto")

    @api.multi
    def run_action(self):
        vehicle = self.env["fleet.vehicle"].browse(self._context.get("active_id"))
        if self.action_type == "quotation":
            sale_line_ref = self.env['sale.order.line']
            car_name = u"Modelo {} \n" \
                       u"Año {} \n" \
                       u"Tipo: {} \n" \
                       u"Nº de asientos: {} \n" \
                       u"Nº de puertas {} \n" \
                       u"Color {} \n" \
                       u"Capacidad del depósito de combustible {} \n" \
                       u"Transmisión {} \n" \
                       u"Tipo de combustible {} \n" \
                       u"CC {} \n".format(vehicle.model_id.name or "",
                                          vehicle.register_year or "",
                                          vehicle.type_id.name or "",
                                          vehicle.seats or "",
                                          vehicle.doors or "",
                                          vehicle.color or "",
                                          vehicle.fueltankcap or "",
                                          vehicle.transmission or "",
                                          vehicle.fuel_type or "",
                                          vehicle.horsepower_tax or ""
                                          )

            order_id = self.env["sale.order"].create({
                "partner_id": self.partner_id.id
            })

            order_lines = order_id.order_line.browse([])
            order_lines += sale_line_ref.new({
                'product_id': 1,
                'price_unit': vehicle.sale_price,
                'product_uom_qty': 1
            })

            for line in order_lines:
                line.product_id_change()
                line._compute_tax_id()
                line.name = car_name

            order_id.order_line = order_lines
            order_id.button_dummy()
            vehicle.sale_ids += order_id

            return {
                'name': u"Cotización",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'view_id': False,
                'target': 'current',
                'views': False,
                'type': 'ir.actions.act_window',
                'res_id': order_id.id,
                'context': self._context
            }
        else:

            payment_dict = {u'payment_date': fields.Date.today(),
                   u'communication': "Avance a {} {}".format(vehicle.model_id.name or "", vehicle.register_year or ""),
                   u'journal_id': self.journal_id.id,
                   u'destination_journal_id': False,
                   u'partner_type': u'customer',
                   u'amount': self.amount,
                   u'payment_type': u'inbound',
                   u'partner_id': self.partner_id.id,
                   u'payment_method_id': 1}

            payment_id = self.env["account.payment"].create(payment_dict)

            payment_id.button_dummy()
            vehicle.payment_ids += payment_id

            return {
                'name': u"Recibo",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'view_id': False,
                'target': 'current',
                'views': False,
                'type': 'ir.actions.act_window',
                'res_id': payment_id.id,
                'context': self._context
            }
