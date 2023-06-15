# -*- coding: utf-8 -*-

import logging
import time
from odoo import fields, models, api, Command, tools, _
from odoo.exceptions import UserError
from lxml import etree

# from lxml_to_dict import lxml_to_dict
# from xmltodict import lxml_to_dict
import xmltodict
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


WECOM_USER_MAPPING_ODOO_USER = {
    "UserID": "wecom_userid",  # 成员UserID
    "Name": "name",  # 成员名称;
    "Department": "",  # 成员部门列表，仅返回该应用有查看权限的部门id
    "MainDepartment": "",  # 主部门
    "IsLeaderInDept": "",  # 表示所在部门是否为上级，0-否，1-是，顺序与Department字段的部门逐一对应
    "DirectLeader": "",  # 直属上级
    "Mobile": "mobile_phone",  # 手机号码
    "Position": "",  # 职位信息
    "Gender": "",  # 企微性别：0表示未定义，1表示男性，2表示女性；odoo性别：male为男性，female为女性，other为其他
    "Email": "work_email",  # 邮箱;
    "Status": "active",  # 激活状态：1=已激活 2=已禁用 4=未激活 已激活代表已激活企业微信或已关注微工作台（原企业号）5=成员退出
    "Avatar": "",  # 头像url。注：如果要获取小图将url最后的”/0”改成”/100”即可。
    "Alias": "",  # 成员别名
    "Telephone": "work_phone",  # 座机;
    "Address": "",  # 地址;
    "ExtAttr": {
        "Type": "",  # 扩展属性类型: 0-本文 1-网页
        "Text": "",  # 文本属性类型，扩展属性类型为0时填写
        "Value": "",  # 文本属性内容
        "Web": "",  # 网页类型属性，扩展属性类型为1时填写
        "Title": "",  # 网页的展示标题
        "Url": "",  # 网页的url
    },  # 扩展属性;
}


class User(models.Model):
    _inherit = ["res.users"]

    # employee_id = fields.Many2one(
    #     "hr.employee",
    #     string="Company employee",
    #     compute="_compute_company_employee",
    #     search="_search_company_employee",
    #     store=True,
    # )  # 变更用户类型时，需要绑定用户，避免出现“创建员工”的按钮，故 store=True

    # ----------------------------------------------------------------------------------
    # 开发人员注意：hr模块中
    # hr.employee.work_email = res.users.email
    # hr.employee.private_email = res.partner.email
    # ----------------------------------------------------------------------------------
    # base 模块中
    # res.user.email = res.partner.email
    # res.user.private_email = res.partner.email
    # ------------------------------------------
    # hr.employee.create() 方法中 创建hr.employee.work_email时会将 res.users.email更新到hr.employee.work_email
    # res.users.write() 方法中 更新res.users.email时会将 res.users.email更新到hr.employee.work_email
    # ------------------------------------------
    # 故重写了 将  private_email = address_home_id.email 修改为 private_email=employee_id.private_email
    # 故重写了 SELF_WRITEABLE_FIELDS
    # ----------------------------------------------------------------------------------

    # private_email = fields.Char(related='employee_id.private_email', string="Private Email")

    def _get_or_create_user_by_wecom_userid(self, object, send_mail, send_message):
        """
        通过企微用户id获取odoo用户
        """
        login = tools.ustr(object.wecom_userid)
        self.env.cr.execute(
            "SELECT id, active FROM res_users WHERE lower(login)=%s", (login,)
        )
        res = self.env.cr.fetchone()
        if res:
            if res[1]:
                return res[0]
        else:
            group_portal_id = self.env["ir.model.data"]._xmlid_to_res_id(
                "base.group_portal"
            )  # 门户用户组
            SudoUser = self.sudo()
            values = {
                "name": object.name,
                "login": login,
                "notification_type": "inbox",
                "groups_id": [(6, 0, [group_portal_id])],
                "share": False,
                "active": object.active,
                "image_1920": object.image_1920,
                "password": self.env["wecomapi.tools.security"].random_passwd(8),
                "company_ids": [(6, 0, [object.company_id.id])],
                "company_id": object.company_id.id,
                "employee_ids": [(6, 0, [object.id])],
                "employee_id": object.id,
                "lang": self.env.lang,
                "company_id": object.company_id.id,
                # 以下为企业微信字段
                "wecom_userid": object.wecom_userid.lower(),
                "wecom_openid": object.wecom_openid,
                "is_wecom_user": object.is_wecom_user,
                "qr_code": object.qr_code,
                "wecom_user_order": object.wecom_user_order,
            }

            # 判断是否已存在 partner
            partner = (
                self.env["res.partner"]
                .sudo()
                .search(
                    [
                        ("wecom_userid", "=", object.wecom_userid),
                        ("company_id", "=", object.company_id.id),
                        ("is_wecom_user", "=", True),
                        "|",
                        ("active", "=", True),
                        ("active", "=", False),
                    ],
                    limit=1,
                )
            )

            if not partner:
                pass
            else:
                values.update({"partner_id": partner.id})
            """
            MailThread功能可以通过上下文键进行一定程度的控制:

            -'mail_create_nosubscribe':在create或message_post上,不要订阅记录线程的uid
            -'mail_create_nolog'：在创建时，不要记录自动的“<Document>“创建”消息
            -'mail_notrack'：在创建和写入时，不要执行值跟踪创建消息
            -'tracking_disable'：在创建和写入时，不执行邮件线程功能（自动订阅、跟踪、发布等）
            -'mail_notify_force_send': 如果要发送的电子邮件通知少于50封,直接发送,而不是使用队列;默认情况下为True
            """
            return (
                SudoUser.with_context(
                    mail_create_nosubscribe=True,
                    mail_create_nolog=True,
                    mail_notrack=True,
                    tracking_disable=True,
                    send_mail=send_mail,
                    send_message=send_message,
                )
                .create(values)
                .id
            )
            # return SudoUser.with_context(send_mail=send_mail).create(values).id

    @api.model_create_multi
    def create(self, vals_list):
        """
        重写以自动邀请用户注册
        send_mail: true 表示发送邀请邮件, false 表示不发送邀请邮件
        批量创建用户时，建议 send_mail=False
        """
        users = super(User, self).create(vals_list)

        if not self.env.context.get("no_reset_password") and self.env.context.get(
            "send_mail"
        ):
            users_with_email = users.filtered("email")
            if users_with_email:
                try:
                    users_with_email.with_context(
                        create_user=True
                    ).action_reset_password()
                except MailDeliveryException:
                    users_with_email.partner_id.with_context(
                        create_user=True
                    ).signup_cancel()

        return users

    # ------------------------------------------------------------
    # 企微部门下载
    # ------------------------------------------------------------
    @api.model
    def download_wecom_contacts(self):
        """
        下载企微通讯录
        """
        start_time = time.time()
        company = self.env.context.get("company_id")

        tasks = []
        if not company:
            company = self.env.company
        if company.is_wecom_organization:
            try:
                wxapi = self.env["wecom.service_api"].InitServiceApi(
                    company.corpid, company.contacts_app_id.secret
                )
                app_config = self.env["wecom.app_config"].sudo()
                contacts_sync_hr_department_id = app_config.get_param(
                    company.contacts_app_id.id, "contacts_sync_hr_department_id"
                )  # 需要同步的企业微信部门ID
                response = wxapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("USER_LIST"),
                    {
                        "department_id": contacts_sync_hr_department_id,
                        "fetch_child": "1",
                    },
                )
            except ApiException as ex:
                end_time = time.time()
                self.env["wecomapi.tools.action"].ApiExceptionDialog(
                    ex, raise_exception=False
                )
                tasks = [
                    {
                        "name": "download_contact_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(ex),
                    }
                ]
            except Exception as e:
                end_time = time.time()
                tasks = [
                    {
                        "name": "download_contact_data",
                        "state": False,
                        "time": end_time - start_time,
                        "msg": str(e),
                    }
                ]
            else:
                wecom_users = response["userlist"]

                # 获取block
                blocks = (
                    self.env["wecom.contacts.block"]
                    .sudo()
                    .search(
                        [
                            ("company_id", "=", company.id),
                        ]
                    )
                )
                block_list = []

                # 生成 block_list
                if len(blocks) > 0:
                    for obj in blocks:
                        if obj.wecom_userid != None:
                            block_list.append(obj.wecom_userid)

                # 从 wecom_users 移除 block_list
                for b in block_list:
                    for item in wecom_users:
                        # userid不区分大小写
                        if item["userid"].lower() == b.lower():
                            wecom_users.remove(item)

                # 1. 下载联系人
                for wecom_user in wecom_users:
                    download_user_result = self.download_user(company, wecom_user)
                    if download_user_result:
                        for r in download_user_result:
                            tasks.append(r)  # 加入设置下载联系人失败结果

                # 2.完成下载
                end_time = time.time()
                task = {
                    "name": "download_contact_data",
                    "state": True,
                    "time": end_time - start_time,
                    "msg": _("Contacts list downloaded successfully."),
                }
                tasks.append(task)
        else:
            end_time = time.time()
            tasks = [
                {
                    "name": "download_contact_data",
                    "state": False,
                    "time": end_time - start_time,
                    "msg": _(
                        "The current company does not identify the enterprise wechat organization. Please configure or switch the company."
                    ),
                }
            ]  # 返回失败结果
        return tasks

    def download_user(self, company, wecom_user):
        """
        下载联系人
        """
        user = self.sudo().search(
            [
                ("wecom_userid", "=", wecom_user["userid"].lower()),
                ("company_id", "=", company.id),
                ("is_wecom_user", "=", True),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )
        result = {}
        app_config = self.env["wecom.app_config"].sudo()
        contacts_allow_add_system_users = app_config.get_param(
            company.contacts_app_id.id, "contacts_allow_add_system_users"
        )  # 允许创建用户

        if contacts_allow_add_system_users == "True":
            contacts_allow_add_system_users = True
        elif contacts_allow_add_system_users is None:
            contacts_allow_add_system_users = False
        else:
            contacts_allow_add_system_users = False

        if not user and contacts_allow_add_system_users:
            result = self.create_user(company, user, wecom_user)
        else:
            result = self.update_user(company, user, wecom_user)
        return result

    def create_user(self, company, user, wecom_user):
        """
        创建联系人
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")

        app_config = self.env["wecom.app_config"].sudo()
        contacts_use_default_avatar = app_config.get_param(
            company.contacts_app_id.id,
            "contacts_use_default_avatar_when_adding_employees",
        )  # 使用系统微信默认头像的标识

        try:
            groups_id = (
                self.sudo()
                .env["res.groups"]
                .search(
                    [
                        ("id", "=", 9),
                    ],
                    limit=1,
                )
                .id
            )  # id=1是内部用户, id=9是门户用户
            user.create(
                {
                    "notification_type": "inbox",
                    "company_ids": [Command.link(user.company_id.id)],
                    "company_id": user.company_id.id,
                    "name": wecom_user["name"],
                    "login": wecom_user["userid"].lower(),  # 登陆账号 使用 企业微信用户id的小写
                    "password": self.env["wecomapi.tools.security"].random_passwd(8),
                    "email": wecom_user["email"],
                    "work_phone": wecom_user["telephone"],
                    "mobile_phone": wecom_user["mobile"],
                    "employee_phone": wecom_user["mobile"],
                    "work_email": wecom_user["email"],
                    "gender": self.env["wecomapi.tools.convert"].sex2gender(
                        wecom_user["gender"]
                    ),
                    "wecom_userid": wecom_user["userid"].lower(),
                    "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                        contacts_use_default_avatar,
                        wecom_user["gender"],
                        wecom_user["avatar"],
                    ),
                    "qr_code": wecom_user["qr_code"],
                    "active": True if wecom_user["status"] == 1 else False,
                    "is_wecom_user": True,
                    "is_company": False,
                    "share": False,
                    "groups_id": [(6, 0, [groups_id])],  # 设置用户为门户用户
                    "tz": "Asia/Shanghai",
                    "lang": "zh_CN",
                }
            )
        except Exception as e:
            result = _("Error creating company %s partner %s %s, error reason: %s") % (
                company.name,
                wecom_user["userid"].lower(),
                wecom_user["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "add_partner",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    def update_user(self, company, user, wecom_user):
        """
        更新联系人
        """
        params = self.env["ir.config_parameter"].sudo()
        debug = params.get_param("wecom.debug_enabled")
        app_config = self.env["wecom.app_config"].sudo()
        contacts_use_default_avatar = app_config.get_param(
            company.contacts_app_id.id,
            "contacts_use_default_avatar_when_adding_employees",
        )  # 使用系统微信默认头像的标识

        try:
            user.write(
                {
                    "notification_type": "inbox",
                    "name": wecom_user["name"],
                    "login": wecom_user["userid"].lower(),  # 登陆账号 使用 企业微信用户id的小写
                    "email": wecom_user["email"],
                    "work_phone": wecom_user["telephone"],
                    "mobile_phone": wecom_user["mobile"],
                    "employee_phone": wecom_user["mobile"],
                    "work_email": wecom_user["email"],
                    "gender": self.env["wecomapi.tools.convert"].sex2gender(
                        wecom_user["gender"]
                    ),
                    "wecom_userid": wecom_user["userid"].lower(),
                    # "image_1920": self.env["wecomapi.tools.file"].get_avatar_base64(
                    #     contacts_use_default_avatar,
                    #     wecom_user["gender"],
                    #     wecom_user["avatar"],
                    # ),
                    "qr_code": wecom_user["qr_code"],
                    "active": True if wecom_user["status"] == 1 else False,
                }
            )
        except Exception as e:
            result = _("Error creating company %s partner %s %s, error reason: %s") % (
                company.name,
                wecom_user["userid"].lower(),
                wecom_user["name"],
                repr(e),
            )
            if debug:
                _logger.warning(result)
            return {
                "name": "update_partner",
                "state": False,
                "time": 0,
                "msg": result,
            }  # 返回失败结果

    # ------------------------------------------------------------
    # 企微通讯录事件
    # ------------------------------------------------------------
    def wecom_event_change_contact_user(self, cmd):
        """
        通讯录事件变更系统用户
        """
        xml_tree = self.env.context.get("xml_tree")
        company_id = self.env.context.get("company_id")
        xml_tree_str = etree.fromstring(bytes.decode(xml_tree))
        dic = lxml_to_dict(xml_tree_str)["xml"]

        domain = [
            "|",
            ("active", "=", True),
            ("active", "=", False),
        ]
        user = self.sudo().search([("company_id", "=", company_id.id)] + domain)
        callback_user = user.search(
            [("wecom_userid", "=", dic["UserID"].lower())] + domain,
            limit=1,
        )
        # print("用户CMD", cmd)
        if callback_user:
            # 如果存在，则更新
            # 用于退出企业微信又重新加入企业微信的员工
            cmd = "update"
        else:
            # 如果不存在且不允许添加系统用户，停止
            app_config = self.env["wecom.app_config"].sudo()
            allow_add_system_users = app_config.get_param(
                company_id.contacts_app_id.id,
                "contacts_allow_add_system_users",
            )  # 使用系统微信默认头像的标识
            if allow_add_system_users is False:
                return

        update_dict = {}

        for key, value in dic.items():
            if (
                key == "ToUserName"
                or key == "FromUserName"
                or key == "CreateTime"
                or key == "Event"
                or key == "MsgType"
                or key == "ChangeType"
            ):
                # 忽略掉 不需要的key
                pass
            else:
                if key in WECOM_USER_MAPPING_ODOO_USER.keys():
                    if WECOM_USER_MAPPING_ODOO_USER[key] != "":
                        if WECOM_USER_MAPPING_ODOO_USER[key] == "wecom_userid":
                            update_dict.update({"wecom_userid": value.lower()})
                        elif WECOM_USER_MAPPING_ODOO_USER[key] == "active":
                            # 状态
                            # 激活状态: 1=已激活，2=已禁用，4=未激活，5=退出企业。
                            # 已激活代表已激活企业微信或已关注微工作台（原企业号）。未激活代表既未激活企业微信又未关注微工作台（原企业号）。
                            if value == "1":
                                update_dict.update({"active": True})
                            else:
                                update_dict.update({"active": False})
                        elif WECOM_USER_MAPPING_ODOO_USER[key] == "gender":
                            gender = self.env["wecomapi.tools.convert"].sex2gender(
                                value
                            )
                            update_dict.update({"gender": gender})
                        else:
                            update_dict[WECOM_USER_MAPPING_ODOO_USER[key]] = value
                else:
                    _logger.info(
                        _(
                            "There is no mapping for field [%s], please contact the developer."
                        )
                        % key
                    )

        if cmd == "create":
            update_dict.update(
                {
                    "is_wecom_user": True,
                }
            )
            try:
                wecomapi = self.env["wecom.service_api"].InitServiceApi(
                    company_id.corpid, company_id.contacts_app_id.secret
                )
                response = wecomapi.httpCall(
                    self.env["wecom.service_api_list"].get_server_api_call("USER_GET"),
                    {"userid": update_dict["wecom_userid"]},
                )
                if response.get("errcode") == 0:
                    update_dict.update({"qr_code": response.get("qr_code")})
            except:
                pass

            callback_user.create(update_dict)
        elif cmd == "update":
            if "wecom_userid" in update_dict:
                del update_dict["wecom_userid"]
            callback_user.write(update_dict)
        elif cmd == "delete":
            callback_user.write(
                {
                    "active": False,
                }
            )


# ------------------------------------------------------------
# 变更用户类型向导
# ------------------------------------------------------------
class ChangeTypeWizard(models.TransientModel):
    _name = "change.type.wizard"
    _description = "Wizard to change user type(WeCom)"

    def _default_user_ids(self):
        user_ids = (
            self._context.get("active_model") == "res.users"
            and self._context.get("active_ids")
            or []
        )
        return [
            (
                0,
                0,
                {
                    "user_id": user.id,
                    "user_login": user.login,
                    "user_name": user.name,
                },
            )
            for user in self.env["res.users"].browse(user_ids)
        ]

    user_ids = fields.One2many(
        "change.type.user", "wizard_id", string="Users", default=_default_user_ids
    )

    def change_type_button(self):
        self.ensure_one()
        self.user_ids.change_type_button()
        if self.env.user in self.mapped("user_ids.user_id"):
            return {"type": "ir.actions.client", "tag": "reload"}
        return {"type": "ir.actions.act_window_close"}


class ChangeTypeUser(models.TransientModel):
    _name = "change.type.user"
    _description = "User, Change Type Wizard"

    wizard_id = fields.Many2one(
        "change.type.wizard", string="Wizard", required=True, ondelete="cascade"
    )

    user_id = fields.Many2one(
        "res.users", string="User", required=True, ondelete="cascade"
    )
    user_login = fields.Char(
        string="Login account",
        readonly=True,
    )
    user_name = fields.Char(string="Login name", readonly=True)
    # 用户类型参见res_group
    new_type = fields.Selection(
        [
            ("1", _("Internal User")),
            ("9", _("Portal User")),
            ("10", _("Public User")),
        ],
        string="User Type",
        default="1",
    )

    def change_type_button(self):
        for line in self:
            if not line.new_type:
                raise UserError(
                    _(
                        "Before clicking the 'Change User Type' button, you must modify the new user type"
                    )
                )
            if (
                # 排除初始系统自带的用户
                line.user_id.id == 1
                or line.user_id.id == 2
                or line.user_id.id == 3
                or line.user_id.id == 4
                or line.user_id.id == 5
            ):
                pass
            else:
                if line.new_type == "1":
                    try:
                        line.user_id.employee_id = (
                            self.env["hr.employee"].search(
                                [
                                    ("id", "in", line.user_id.employee_ids.ids),
                                    ("company_id", "=", line.user_id.company_id.id),
                                ],
                                limit=1,
                            ),
                        )
                    except Exception as e:
                        print("用户 %s 类型变更错误,错误:%s" % (line.user_id.name, repr(e)))

                line.user_id.write({"groups_id": [(6, 0, line.new_type)]})
        self.write({"new_type": False})
