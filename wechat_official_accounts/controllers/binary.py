# -*- coding: utf-8 -*-

import base64
import functools
import io
import odoo

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

from odoo import http, _
from odoo.http import request, Response
from odoo.modules import get_resource_path
from odoo.modules.registry import Registry
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.web.controllers.binary import Binary # type: ignore

class WechatOfficialAccountsQrCodeBinary(Binary):
    @http.route([
        '/web/binary/wechat_official_accounts',
        '/wechat_official_accounts',
        '/wechat_official_accounts.png',
    ], type='http', auth="none", cors="*")
    def company_wechat_official_accounts_qrcode(self, dbname=None, **kw):
        """
        获取二维码图片
        """
        imgname = 'qrcode'
        imgext = '.png'
        placeholder = functools.partial(get_resource_path, 'wechat_official_accounts', 'static', 'src', 'img')
        dbname = request.db
        uid = (request.session.uid if dbname else None) or odoo.SUPERUSER_ID

        if not dbname:
            response = http.Stream.from_path(placeholder(imgname + imgext)).get_response()
        else:
            try:
                registry = Registry(dbname)
                with registry.cursor() as cr:
                    company = int(kw['company']) if kw and kw.get('company') else False

                    if company:
                        cr.execute("""SELECT social_wechat_official_accounts, write_date
                                        FROM res_company
                                       WHERE id = %s
                                   """, (company,))
                    else:
                        cr.execute("""SELECT c.social_wechat_official_accounts, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                                   """, (uid,))
                    row = cr.fetchone()

                    if row and row[0]:
                        image_base64 = base64.b64decode(row[0])
                        image_data = io.BytesIO(image_base64)
                        mimetype = guess_mimetype(image_base64, default='image/png')
                        imgext = '.' + mimetype.split('/')[1]
                        if imgext == '.svg+xml':
                            imgext = '.svg'
                        response = send_file(
                            image_data,
                            request.httprequest.environ,
                            download_name=imgname + imgext,
                            mimetype=mimetype,
                            last_modified=row[1],
                            response_class=Response,
                        )
                    else:
                        response = http.Stream.from_path(placeholder('qrcode.png')).get_response()
            except Exception:
                response = http.Stream.from_path(placeholder(imgname + imgext)).get_response()

        return response