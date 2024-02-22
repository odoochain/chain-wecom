# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools, Command
from odoo.exceptions import UserError
from odoo.osv import expression

class WechatComposeMessage(models.TransientModel):
    """
    撰写微信消息向导
    """
    _name = 'wechat.compose.message'
    _description = 'Wechat message composition wizard'
    _log_access = True

    @api.model
    def default_get(self, fields):
        result = super(WechatComposeMessage, self).default_get(fields)
        if 'model' in fields and 'model' not in result:
            result['model'] = self._context.get('active_model')
        if 'res_id' in fields and 'res_id' not in result:
            result['res_id'] = self._context.get('active_id')
        if set(fields) & set(['model', 'res_id', 'partner_ids', 'record_name', 'subject']):
            result.update(self.get_record_data(result))
        if 'create_uid' in fields and 'create_uid' not in result:
            result['create_uid'] = self.env.uid

        filtered_result = dict((fname, result[fname]) for fname in result if fname in fields)
        return filtered_result

    def _partner_ids_domain(self):
        return expression.OR([
            [('type', '!=', 'private')],
            [('id', 'in', self.env.context.get('default_partner_ids', []))],
        ])

    # 接受者
    partner_ids = fields.Many2many(
        'res.partner', 'wechat_compose_message_res_partner_rel',
        'wizard_id', 'partner_id', 'Additional Contacts',
        domain=_partner_ids_domain)

    # 内容
    subject = fields.Char('Subject', compute=False)
    template_id = fields.Many2one('wechat.message_templates', 'Use template', domain="[('model', '=', model)]")


    # 源
    author_id = fields.Many2one('res.partner', 'Author',)

    # 合成
    model = fields.Char('Related Document Model')
    res_id = fields.Integer('Related Document ID')
    record_name = fields.Char('Message Record Name')

    @api.model
    def get_record_data(self, values):
        result, subject = {}, False
        if values.get('model') and values.get('res_id'):
            doc_name_get = self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name'] = doc_name_get and doc_name_get[0][1] or ''
            subject = tools.ustr(result['record_name'])

        result['subject'] = subject

        return result

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------
    def action_send_wenchat_message(self):
        """
        处理向导内容，并继续发送相关消息，如果需要，实时呈现任何模板模式。
        """
        model_description = self._context.get('model_description')