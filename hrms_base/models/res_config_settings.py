# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    del_wecom_tag = fields.Boolean(
        string="Delete wecom tag",
        default=False
    )

    module_hrms_recruitment = fields.Boolean(
        string="Employee Recruitment",
        help='Helps you to manage recruitment  Management.\n'
             '- This installs the module recruitment  Management.'
    )
    module_hrms_holidays = fields.Boolean(
        string="Employee Holidays",
        default=False
    )
    module_hrms_attendance = fields.Boolean(string="Employee Attendances", default=False)
    module_hrms_expense = fields.Boolean(string="Employee Expenses", default=False)
    module_hrms_empowerment = fields.Boolean(string="Employee Empowerment", default=False)

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

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        del_wecom_tag = (
            True if ir_config.get_param("wecom.del_wecom_tag") == "True" else False
        )
        module_hrms_recruitment = (
            True if ir_config.get_param("wecom.module_hrms_recruitment") == "True" else False
        )
        res.update(
            del_wecom_tag=del_wecom_tag,
            module_hrms_recruitment=module_hrms_recruitment,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wecom.del_wecom_tag", self.del_wecom_tag or "False")
        ir_config.set_param("wecom.module_hrms_recruitment", self.module_hrms_recruitment or "False")

    def hide_hr_menu(self):
        """
        一键隐藏HR菜单
        :return:
        """
        domain = [
            "&",
            "&",
            "&",
            ("parent_id", "=", False),
            ("web_icon", "ilike", "hr"),
            ("name", "not like", "HRM"),
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]

        self.env["ir.ui.menu"].search(domain).sudo().write({"active": False})
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
