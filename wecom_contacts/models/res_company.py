# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo.http import request
from odoo import api, fields, models, tools, _
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    # 通讯录
    contacts_app_id = fields.Many2one(
        "wecom.apps",
        string="Contacts Application",
        # required=True,
        # default=lambda self: self.env.company,
        domain="[('company_id', '=', current_company_id)]",
    )

    wecom_contacts_join_qrcode_enabled = fields.Boolean(
        string="Enable to join the enterprise QR code",
        default=True,
        copy=False,
    )
    wecom_contacts_join_qrcode = fields.Char(
        string="Join enterprise wechat QR code",
        copy=False,
        readonly=True,
    )
    wecom_contacts_join_qrcode_size_type = fields.Selection(
        [
            ("1", "171px x 171px"),
            ("2", "399px x 399px"),
            ("3", "741px x 741px"),
            ("4", "2052px x 2052px"),
        ],
        string="Join enterprise wechat QR code  size type",
        default="2",
        required=True,
    )
    wecom_contacts_join_qrcode_last_time = fields.Datetime(
        string="Get the last time of QR code (UTC)",
        copy=False,
    )

    def cron_get_corp_jsapi_ticket(self):
        """
        定时任务，每隔两小时更新企业的jsapi_ticket
        """
        for company in self:
            if (
                company.is_wecom_organization
                and company.corpid
                and company.contacts_app_id
            ):
                _logger.info(
                    _("Automatic tasks:Start getting JSAPI ticket for company [%s]")
                    % (company.name)
                )
                if (
                    company.wecom_jsapi_ticket_expiration_time
                    and company.wecom_jsapi_ticket_expiration_time > datetime.now()
                ):
                    _logger.info(
                        _(
                            "The company [%s] ticket is still valid and does not need to be updated!"
                        )
                        % (company.name)
                    )
                else:
                    try:
                        wecom_api = self.env["wecom.service_api"].InitServiceApi(
                            self.company_id.corpid, self.contacts_app_id.secret
                        )
                        response = wecom_api.httpCall(
                            self.env["wecom.service_api_list"].get_server_api_call(
                                "GET_JSAPI_TICKET"
                            ),
                            {},
                        )
                    except ApiException as ex:
                        _logger.error(
                            _("Error in obtaining company [%s] ticket, reason: %s")
                            % (company.name, ex)
                        )
                    else:
                        if response["errcode"] == 0:
                            company.write(
                                {
                                    "wecom_jsapi_ticket": response["ticket"],
                                    "wecom_jsapi_ticket_expiration_time": datetime.now()
                                    + timedelta(seconds=response["expires_in"]),
                                }
                            )
                    finally:
                        _logger.info(
                            _("Automatic tasks:End of company [%s] JSAPI ticket update")
                            % (company.name)
                        )
