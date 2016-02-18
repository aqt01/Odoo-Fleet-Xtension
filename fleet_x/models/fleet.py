# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from openerp import SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, date


class fleet_vehicle_type(models.Model):
    _name = "fleet.vehicle.type"

    name = fields.Char(_('Name'), requried=True, selectable=False)


class fleet_vehicle_odometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    _order = 'value desc'

    def _get_neighbours(self):
        '''
        get the odometer reading 
        @todo: since this field is stored, we should recompute in instances of  
        another reading being inserted just before this 
        '''
        previous = self.search([('vehicle_id', '=', self.vehicle_id.id),
                                ('id', '!=', self.id),
                                ('date', '<=', self.date)],
                               limit=1, order='date desc,value desc')
        next = self.search([('vehicle_id', '=', self.vehicle_id.id),
                            ('id', '!=', self.id),
                            ('date', '>=', self.date)],
                           limit=1, order='date asc,value asc')
        return previous, next

    @api.constrains('value')
    def _check_meter_value(self):
        '''
        let's ensure that odo value increases with every new one logged
        '''
        previous, next = self._get_neighbours()
        if len(previous) and previous.value != next.value:
            if previous.value > self.value:
                raise Warning(
                    _('Odometer reading can not be lesser than the last recorded odometer reading for this vehicle'))
            if next.value < self.value:
                raise Warning(
                    _('Odometer reading can not be greater than the next recorded odometer reading for this vehicle'))
        return True


class fleet_vehicle_location(models.Model):
    _name = "fleet.vehicle.location"

    name = fields.Char(_('Name'), required=True)


class fleet_vehicle_department(models.Model):
    _name = 'fleet.vehicle.department'

    @api.one
    @api.depends("vehicle_ids")
    def _get_vehicle_count(self):
        self.vehicle_count = len(self.vehicle_ids)

    @api.one
    @api.depends('name', 'parent_id')
    def _dept_name_get_fnc(self):
        name = self.name
        if self.parent_id:
            name = self.parent_id.name + ' / ' + name
        self.display_name = name

    name = fields.Char(_('Name'), required=True)
    display_name = fields.Char(compute='_dept_name_get_fnc', string=_('Name'), store=True)
    vehicle_ids = fields.One2many('fleet.vehicle', 'department_id', _('Vehicles'))
    vehicle_count = fields.Integer('Vehicle Count', compute="_get_vehicle_count")
    parent_id = fields.Many2one('fleet.vehicle.department', _('Parent Department'), select=True)
    child_ids = fields.One2many('fleet.vehicle.department', 'parent_id', _('Child Departments'))
    note = fields.Text('Note')

    @api.multi
    def name_get(self):
        result = []
        for department in self:
            result.append((department.id, department.display_name))
        return result

    @api.constrains('parent_id')
    @api.multi
    def _check_recursion(self):
        level = 100
        cr = self.env.cr
        while len(self.ids):
            cr.execute('select distinct parent_id from fleet_vehicle_department where id IN %s', (tuple(self.ids),))
            ids = filter(None, map(lambda x: x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True


class fleet_vehicle(models.Model):
    _inherit = "fleet.vehicle"
    _order = 'license_plate asc'

    sale_ids = fields.One2many("sale.order", "vehicle_id", string="Cotizaciones")
    payment_ids = fields.One2many("account.payment", "vehicle_id", string="Pagos")
    transmission = fields.Selection([('manual', 'Manual'), ('automatic', 'Automatic'), ('rictronic', 'Trictronic')], 'Transmission', help='Transmission Used by the vehicle')
    odometer_ids = fields.One2many('fleet.vehicle.odometer', 'vehicle_id',
                                   _('Odometers'), readonly=1)
    cost_ids = fields.One2many('fleet.vehicle.cost', 'vehicle_id', _('Cost'),
                               readonly=1)
    department_id = fields.Many2one('fleet.vehicle.department', _('Department'),
                                    help=_('Department of the vehicle'),
                                    index=1, track_visibility='onchange')
    attachment_count = fields.Integer(string=_('Number of Attachments'),
                                      compute='_get_attachment_number')
    note = fields.Text(_('Internal Note'))
    active = fields.Boolean(_('Active'), default=True, index=True)

    odometer_date = fields.Date(_('Odometer Date'), readonly=True,
                                compute='_get_odometer_date', store=False)

    # properties
    manufacture_year = fields.Char(_('Year of Manufacture'), size=4)
    register_year = fields.Char(u'Matriculación', size=4)
    ownership = fields.Many2one("res.partner", _('Ownership'), required=False)
    fueltankcap = fields.Float(_('Fuel Tank Capacity'))
    acquisition_date = fields.Date(_('Acquisition Date'), required=True,
                                   help=_('Date of purchase'),
                                   default=fields.Date.today())
    type_id = fields.Many2one('fleet.vehicle.type', _('Type'), required=True)
    location_id = fields.Many2one('fleet.vehicle.location',
                                  _('Operational Location'))

    # statistics
    lmiles = fields.Float(_('Miles per year'), compute="_compute_vehicle_stats",
                          readonly=True, store=True)
    distance = fields.Float(_('Distance covered since purchase'),
                            compute="_compute_vehicle_stats", readonly=True, store=True)
    costpm = fields.Float(_('Cost/KM'), compute="_compute_vehicle_stats",
                          readonly=True, store=True)
    costpmon = fields.Float(_('Cost/Mnth'), compute="_compute_vehicle_stats",
                            readonly=True, store=True)
    costtotal = fields.Float(_('Total Cost'), compute="_compute_vehicle_stats",
                             readonly=True, store=True)

    # purchase info
    ppartner = fields.Many2one('res.partner', _('Purchased From'),
                               domain="[('supplier','=',True)]")
    car_value = fields.Float(_('Purchase Price'), help=_('Value of the bought vehicle'))
    podometer = fields.Integer(_('Odometer at Purchase'),
                               inverse="_set_odometer_at_purchase")
    warrexp = fields.Date('Date', help=_("Expiry date of warranty"))
    warrexpmil = fields.Integer(_('(or) Kilometer'), help=_("Expiry Kilometer of warranty"))
    license_plate = fields.Char('License Plate', required=False, help='License plate number of the vehicle (ie: plate number for a car)', copy=False)
    vin_sn = fields.Char('Chassis Number', required=True, help='Unique number written on the vehicle motor (VIN/SN number)', copy=False)
    sale_price = fields.Float("Precio de venta")

    _sql_constraints = [
        ('uniq_license_plate', 'unique(license_plate)', _('The registration # of the vehicle must be unique !')),
        ('uniq_vin', 'unique(vin_sn)', _('The Chassis # of the vehicle must be unique !'))
    ]

    @api.one
    def _get_odometer_date(self):
        # date of last odometer reading   
        if len(self.odometer_ids):
            self.odometer_date = self.odometer_ids.sorted(lambda r: r.value)[-1].date

    @api.one
    @api.depends('acquisition_date', 'podometer', 'odometer', 'odometer_ids', 'cost_ids', 'cost_ids.amount')
    def _compute_vehicle_stats(self):
        if not isinstance(self.id, int):
            return
        costpm = 0.0
        costpmon = 0.0
        costtotal = 0.0
        if not len(self.odometer_ids):
            return
        odoo_delta = self.odometer - self.odometer_ids.sorted(lambda r: r.value)[0].value
        if odoo_delta <= 0:
            return
        self.distance = odoo_delta
        if not len(self.cost_ids) or not self.acquisition_date:
            return

        time_delta = relativedelta(datetime.now(), fields.Date.from_string(self.acquisition_date))
        # distance traveled since the first odometer was logged

        for cost in self.cost_ids:
            costtotal += cost.amount

        months = (time_delta.years * 12) + time_delta.months
        costpmon = months and costtotal / months or costtotal
        costpm = costtotal / odoo_delta

        self.costpm = costpm
        self.costpmon = costpmon
        self.costtotal = costtotal
        self.lmiles = (time_delta.years > 1) and odoo_delta / time_delta.years or odoo_delta

    @api.one
    def _set_odometer_at_purchase(self):
        if not len(self.odometer_ids):
            self.env['fleet.vehicle.odometer'].create({
                'value': self.podometer,
                'vehicle_id': self.id,
                'date': self.acquisition_date
            })
        else:
            first = self.odometer_ids[-1]
            first_dt = fields.Date.from_string(first.date)
            acquisition_dt = fields.Date.from_string(self.acquisition_date)
            if first_dt <= acquisition_dt:
                first.write({'value': self.podometer,
                             'date': self.acquisition_date})
            else:
                self.env['fleet.vehicle.odometer'].create({
                    'value': self.podometer,
                    'vehicle_id': self.id,
                    'date': self.acquisition_date
                })

    @api.one
    def _get_attachment_number(self):
        '''
        returns the number of attachments attached to a record
        FIXME: not working well for classes that inherits from this
        '''
        self.attachment_count = self.env['ir.attachment'].search_count([('res_model', '=', self._name),
                                                                        ('res_id', '=', self.id)])

    def action_get_attachment_tree_view(self, cr, uid, ids, context=None):
        model, action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'action_attachment')
        action = self.pool.get(model).read(cr, uid, action_id, context=context)
        action['context'] = {'default_res_model': self._name, 'default_res_id': ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name), ('res_id', 'in', ids)])
        return action


class fleet_vehicle_model(models.Model):
    _inherit = 'fleet.vehicle.model'
    vendors = fields.Many2many('res.partner', 'fleet_vehicle_model_vendors',
                               'model_id', 'partner_id', string=_('Vendors'),
                               domain="[('supplier','=',True)]")


# --------------
# Vehicle Department
# --------------

class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    ref = fields.Char(readonly=True)
    vehicle_type_id = fields.Many2one('fleet.vehicle.type', _('Vehicle Type'), related='vehicle_id.type_id', readonly=True,
                                      store=True)
    vehicle_location_id = fields.Many2one('fleet.vehicle.location', _('Vehicle Location'),
                                          related='vehicle_id.location_id', readonly=True, store=True)

    @api.model
    def create(self, values):
        vehicle_id = values.get("vehicle_id", False)

        if self._context.get("active_model", False) == "fleet.vehicle":
            vehicle_id = self.env["fleet.vehicle"].browse(self._context.get("active_id")).id

        if vehicle_id:
            vehicle = self.env['fleet.vehicle'].browse(vehicle_id)


        values['ref'] = '%s-%s' % (vehicle.license_plate, self.env['ir.sequence'].next_by_code('fleet_vehicle_cost_ref'))
        return super(fleet_vehicle_cost, self).create(values)
