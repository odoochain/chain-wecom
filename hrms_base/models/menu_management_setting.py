from odoo import api, models, fields


class HrmsSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    del_wecom_tag = fields.Boolean(
        string="Delete wecom tag",
        default=False
    )
    # order_menu = fields.Boolean(default=False, string='Order Menu Alphabets')

    @api.model
    def get_values(self):
        """ Get values for fields in the settings
         and assign the value to the fields"""

        res = super(HrmsSettings, self).get_values()
        ir_config = self.env["ir.config_parameter"].sudo()

        del_wecom_tag = (
            True if ir_config.get_param("wecom.del_wecom_tag") == "True" else False
        )

        res.update(
            del_wecom_tag=del_wecom_tag,
        )
        return res

    def set_values(self):
        super(HrmsSettings, self).set_values()
        ir_config = self.env["ir.config_parameter"].sudo()
        ir_config.set_param("wecom.del_wecom_tag", self.del_wecom_tag or "False")

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

    # @api.model
    # def get_values(self):
    #     """ Get values for fields in the settings
    #      and assign the value to the fields"""
    #     res = super(HrmsSettings, self).get_values()
    #     params = self.env['ir.config_parameter'].sudo()
    #     order_menu = params.get_param('order_menu', default=False)
    #     res.update(
    #         order_menu=order_menu,
    #     )
    #     return res
    #
    # def set_values(self):
    #     """ save values in  the settings fields"""
    #     super(HrmsSettings, self).set_values()
    #     self.env['ir.config_parameter'].sudo().set_param("order_menu",  self.order_menu)
    #
    # @api.onchange('order_menu')
    # def onchange_order_menu(self):
    #     asc_order_menu = self.env['ir.config_parameter'].sudo().get_param('order_menu') or False
    #     sqno = 1
    #     if asc_order_menu:
    #         # menus = self.env['ir.ui.menu'].sudo().search([('parent_id','=', False),('name', 'not in', ['Apps', 'Settings', 'Dashboard'])], order='name ASC')
    #         menus = self.env['ir.ui.menu'].sudo().search(['&',('parent_id','=', False),('name','not in',('Apps','Settings','Dashboard'))])
    #         for menu in menus:
    #             if not menu.order_changed:
    #                 menu.recent_menu_sequence = menu.sequence
    #                 menu.sequence = sqno
    #                 menu.order_changed = True
    #                 sqno += 1
    #     else:
    #         menus = self.env['ir.ui.menu'].search([('parent_id', '=', False), ('name', 'not in', ('Apps', 'Settings', 'Dashboard'))])
    #
    #         for menu in menus:
    #             if menu.order_changed:
    #                 menu.sequence = menu.recent_menu_sequence
    #                 menu.recent_menu_sequence = 0
    #                 menu.order_changed = False
    #
    #     return False

