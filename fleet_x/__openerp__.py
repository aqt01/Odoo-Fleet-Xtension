# -*- coding: utf-8 -*-
{
    'name': "Fleet Xtenson",
    'summary': "This is an extension of default Fleet Management module",
    'author': "Salton Massally <smassally@idtlabs.sl>",
    'website': "http://idtlabs.sl",
    'category': 'Managing vehicles and contracts',
    'version': '0.1',
    'depends': ['base', 'sale', 'fleet', 'board', 'product', 'stock'],
    'data': [
        'data/fleet_data.xml',
        'wizard/action_wizard_view.xml',
        'security/ir.model.access.csv',
        'views/fleet.xml',
        'views/fleet_board_view.xml',
        'views/product_view.xml',

    ],
    'installable': True

}
