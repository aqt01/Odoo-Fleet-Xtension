# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api, _


class fleet_config_settings(models.TransientModel):
    _inherit = 'fleet.config.settings'

    default_analytic_account_id = fields.Many2one('account.analytic.account', _('Analytic Account'))
    default_account_debit = fields.Many2one('account.account', _('Debit Account'))
    default_account_credit = fields.Many2one('account.account', _('Credit Account'))
    default_journal_id = fields.Many2one('account.journal', _('Journal'))

    # @api.one
    # def get_default_default_analytic_account_id(self):
    #     res = self.env["ir.config_parameter"].get_param("fleet.default_analytic_account_id")
    #     self.default_analytic_account_id = res or None
    #
    # @api.one
    # def set_default_analytic_account_id(self):
    #     self.env["ir.config_parameter"].set_param("fleet.default_analytic_account_id",
    #                                               self.default_analytic_account_id.id or None)
    #
    # @api.one
    # def get_default_default_account_debit(self):
    #     res = self.env["ir.config_parameter"].get_param("fleet.default_account_debit")
    #     self.default_account_debit = res or None
    #
    # @api.one
    # def set_default_account_debit(self):
    #     self.env["ir.config_parameter"].set_param("fleet.default_account_debit",
    #                                               self.default_account_debit.id or None)
    #
    # @api.one
    # def get_default_default_account_credit(self):
    #     if self:
    #         res = self.env["ir.config_parameter"].get_param("fleet.default_account_credit")
    #         self.default_account_credit = res or None
    #
    # @api.one
    # def set_default_account_credit(self):
    #     self.env["ir.config_parameter"].set_param("fleet.default_account_credit",
    #                                               self.default_account_credit.id or None)
    #
    # @api.one
    # def get_default_default_journal_id(self):
    #     res = self.env["ir.config_parameter"].get_param("fleet.default_journal_id")
    #     self.default_journal_id = res or None
    #
    # @api.one
    # def set_default_journal_id(self):
    #     self.env["ir.config_parameter"].set_param("fleet.default_journal_id",
    #                                               self.default_journal_id.id or None)
