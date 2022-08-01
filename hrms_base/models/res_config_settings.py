# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_hrms_recruitment = fields.Boolean(
        string="Employee Recruitment",
        config_parameter='hrms_base.module_hrms_recruitment',
        help='Helps you to manage recruitment  Management.\n'
             '- This installs the module recruitment  Management.'
    )
    module_hrms_holidays = fields.Boolean(
        string="Employee Holidays",
        help='Helps you to manage holidays  Management.\n'
             '- This installs the module holidays  Management.'
    )
    module_hrms_attendance = fields.Boolean(string="Employee Attendances", config_parameter='hrms_base'
                                                                                            '.module_hrms_attendance')
    module_hrms_expense = fields.Boolean(string="Employee Expenses")
    module_hrms_empowerment = fields.Boolean(string="Employee Empowerment")

    test_module_hrms_recruitment = fields.Boolean(default=False, invisible=True)
    test_module_hrms_holidays = fields.Boolean(default=False, invisible=True)
    test_module_hrms_attendance = fields.Boolean(default=False, invisible=True)
    test_module_hrms_expense = fields.Boolean(default=False, invisible=True)
    test_module_hrms_empowerment = fields.Boolean(default=False, invisible=True)

    @api.onchange('module_hrms_recruitment')
    def onchange_module_hrms_recruitment(self):
        for each in self:
            if each.module_hrms_recruitment:
                if not self.env['ir.module.module'].search([('name', '=', 'hrms_recruitment')]):
                    each.test_module_hrms_recruitment = True
                    each.module_hrms_recruitment = False
                else:
                    each.test_module_hrms_recruitment = False

    @api.onchange('module_hrms_holidays')
    def onchange_module_hrms_holidays(self):
        for each in self:
            if each.module_hrms_holidays:
                if not self.env['ir.module.module'].search([('name', '=', 'hrms_holidays')]):
                    each.test_module_hrms_holidays = True
                    each.module_hrms_holidays = False
                else:
                    each.test_module_hrms_holidays = False

    @api.onchange('module_hrms_attendance')
    def onchange_module_hrms_attendance(self):
        for each in self:
            if each.module_hrms_attendance:
                if not self.env['ir.module.module'].search([('name', '=', 'hrms_attendance')]):
                    each.test_module_hrms_attendance = True
                    each.module_hrms_attendance = False
                else:
                    each.test_module_hrms_attendance = False

    @api.onchange('module_hrms_expense')
    def onchange_module_hrms_expense(self):
        for each in self:
            if each.module_hrms_expense:
                if not self.env['ir.module.module'].search([('name', '=', 'hrms_expense')]):
                    each.test_module_hrms_expense = True
                    each.module_hrms_expense = False
                else:
                    each.test_module_hrms_expense = False

    @api.onchange('module_hrms_empowerment')
    def onchange_module_hrms_empowerment(self):
        for each in self:
            if each.module_hrms_empowerment:
                if not self.env['ir.module.module'].search([('name', '=', 'hrms_empowerment')]):
                    each.test_module_hrms_empowerment = True
                    each.module_hrms_empowerment = False
                else:
                    each.test_module_hrms_empowerment = False


