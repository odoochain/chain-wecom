from odoo.models import api, Model
from odoo.tools.safe_eval import const_eval


class HrmsIrConfigParameter(Model):
    _inherit = "ir.config_parameter"

    @api.model
    def get_hrms_config(self):
        get_param = self.sudo().get_param
        return {
            'module_hrms_attendance': const_eval(get_param("hrms_base.module_hrms_attendance", 'False')),
        }
