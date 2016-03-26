# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp.tools.translate import _

class fleet_vehicle_gallery(models.Model):    
    _name = 'fleet.vehicle.gallery'
    _order = "name DESC,id"
    
    name = fields.Datetime(_('Date'), requried=True, default=fields.Date.today())
    vehicle_id = fields.Many2one('fleet.vehicle', requried=True, ondelete='cascade')
    
    front_view = fields.Binary(_('Front View'), requried=True)
    left_side_view = fields.Binary(_('Left Side View'), requried=True)
    right_side_view = fields.Binary(_('Right Side View'), requried=True)
    rear_view = fields.Binary(_('Rear View'), requried=True)
    odometer_view = fields.Binary(_('Odometer View'), requried=True)

    doc_type = fields.Selection([("in", "CONOCIMIENTO DE RECIBO"), ("in", "CONOCIMIENTO DE ENTREGA")], string="Tipo de conduce", required=True)
    to_partner_id = fields.Many2one("res.partner", "Sirvase entregar vehiculo descrito abajo a", required=True)
    from_partner_id = fields.Many2one("res.partner", "Para recibir de", required=True)
    description = fields.Many2many("gallery.descriptions", string="Concepto de entrega")


    internal_mirror = fields.Boolean("Espejo retrovisor interno")
    right_mirror = fields.Boolean("Espejo retrovisor derecho")
    left_mirror = fields.Boolean("Espejo retrovisor izquierdo")
    fuel_plug = fields.Boolean(u"Tapón de gasolina")
    radiator_plug = fields.Boolean(u"Tapón del raiador")
    radio = fields.Boolean("Radio")
    gato = fields.Boolean("Gato")
    tire = fields.Selection([("new", "Nuevas"),("used","Usadas")],"Gomas")
    r_tire = fields.Selection([("new", "Nuevas"),("used","Usadas")],"Goma de repuesta")
    carpet = fields.Boolean(u"Alfómbra")
    kit = fields.Boolean(u"Botiquin")
    lighter = fields.Boolean(u"Encendedor")
    front_turn_lamp = fields.Boolean(u"Luces direccionales delanteras")
    back_turn_lamp = fields.Boolean(u"Luces direccionales traseras")
    manual = fields.Boolean(u"Manual del usuario")
    keys = fields.Boolean(u"Duplicado llave de encendido")
    wheel_wrench = fields.Boolean(u"LLave de rueda")


class GalleryDescriptions(models.Model):
    _name = "gallery.descriptions"

    name = fields.Char()

class fleet_vehicle(models.Model):
    _inherit = "fleet.vehicle"
    
    gallery_ids = fields.One2many('fleet.vehicle.gallery', 'vehicle_id', _('Gallaries'),
                                          readonly=True)
    gallery_count = fields.Integer(_('Gallery Count'), compute='_get_gallery_count', readonly=True)
    
    @api.one
    @api.depends('gallery_ids')
    def _get_gallery_count(self):
        self.gallery_count = len(self.gallery_ids)