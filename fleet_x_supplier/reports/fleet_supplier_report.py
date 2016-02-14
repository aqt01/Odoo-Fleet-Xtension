import time
import datetime
from dateutil.relativedelta import relativedelta

from openerp import tools, _
from openerp.osv import fields, osv


class report_fleet_supplier(osv.osv):
    _name = "report.fleet.supplier"
    _description = "Fleet Supplier"
    _auto = False
    _columns = {
        'id': fields.integer('ID'),
        'vendor_id': fields.many2one('res.partner', _('Supplier'), required=True, readonly=True),
        'date': fields.date(_('Date Logged')),
        'vehicle_id': fields.many2one('fleet.vehicle', _('Vehicle'), required=True,
                                      help=_('Vehicle concerned by this log')),
        'cost_subtype_id': fields.many2one('fleet.service.type', _('Type'),
                                           help=_('Cost type purchased with this cost')),
        'amount': fields.float(_('Total Amount')),
        'cost_type': fields.selection(
            [('contract', _('Contract')), ('services', _('Services')), ('fuel', _('Fuel')), ('other', _('Other'))],
            _('Category of the cost'), help=_('For internal purpose only'), required=True),
        'nbr': fields.integer('Count', readonly=True),

    }
    _order = 'amount desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_fleet_supplier')
        cr.execute("""
            create or replace view report_fleet_supplier as (
                SELECT 
                    min(c.id) as id, 
                    s.vendor_id as vendor_id, 
                    c.date as date, 
                    c.vehicle_id as vehicle_id, 
                    c.cost_subtype_id as cost_subtype_id, 
                    c.amount as amount, 
                    c.cost_type as cost_type,
                    count(c.id) as nbr
                FROM
                    (
                        SELECT 
                            vendor_id as vendor_id, cost_id as cost_id
                        FROM 
                            fleet_vehicle_log_fuel
                        UNION ALL
                        SELECT 
                            vendor_id as vendor_id, cost_id as cost_id
                        FROM 
                            fleet_vehicle_log_services
                        UNION ALL
                        SELECT 
                            insurer_id as vendor_id, cost_id as cost_id
                        FROM 
                            fleet_vehicle_log_contract
                    ) as s
                INNER JOIN
                    fleet_vehicle_cost as c on s.cost_id=c.id
                GROUP BY
                    s.vendor_id, c.date, c.vehicle_id, c.cost_subtype_id, c.amount, c.cost_type
            )""")
