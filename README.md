Odoo-Fleet-Xtension
===================

Extends odoo fleet module providing the following:
* Driver Management
* Fuel Management
* Service Management (unfinished)
* Supplier Management
* Issue Management
* Integration with account
* etc...


INSTALL
===================

1.- Create custom_module directory on your odoo folder installation

$ mkdir /opt/odoo/custom_modules ( or create custom_modules on your odoo install location)
$ cd /opt/odoo/custom_modules/
$ git clone https://github.com/eneldoserrata/Odoo-Fleet-Xtension
 
2.- Edit addons_path to point to the custom_modules created above

# Edit custom path to point custom modules

Add the path to odoo addons path created above
$ vim ~/.openerp_serverrc ( Must be in the home directory of the user that runs the odoo server )

Add the path to '/opt/odoo/custom_modules' in the line 'addons_path' separated by comma

Example
...
addons_path=/opt/odoo/addons,/opt/odoo/custom_modules/Odoo-Fleet-Xtension
...

3.- Restart your odoo server and update the app list 

To update the app list, you must be in developer mode, and follow the steps in [this link](http://stackoverflow.com/questions/27124806/where-is-update-modules-list-in-odoo-v8)




