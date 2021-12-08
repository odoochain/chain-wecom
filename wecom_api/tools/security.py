# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
import base64
import random
import hashlib
import time
import struct
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET
import socket
import hashlib
import werkzeug.urls
import werkzeug.utils

_logger = logging.getLogger(__name__)

#########################################################################
# Description:定义错误码含义
#########################################################################
WXBizMsgCrypt_OK = 0
WXBizMsgCrypt_ValidateSignature_Error = -40001
WXBizMsgCrypt_ParseXml_Error = -40002
WXBizMsgCrypt_ComputeSignature_Error = -40003
WXBizMsgCrypt_IllegalAesKey = -40004
WXBizMsgCrypt_ValidateCorpid_Error = -40005
WXBizMsgCrypt_EncryptAES_Error = -40006
WXBizMsgCrypt_DecryptAES_Error = -40007
WXBizMsgCrypt_IllegalBuffer = -40008
WXBizMsgCrypt_EncodeBase64_Error = -40009
WXBizMsgCrypt_DecodeBase64_Error = -40010
WXBizMsgCrypt_GenReturnXml_Error = -40011


class FormatException(Exception):
    pass


def throw_exception(message, exception_class=FormatException):
    """自定义引发异常函数"""
    raise exception_class(message)


class SHA1:
    """计算企业微信的消息签名接口"""

    def getSHA1(self, token, timestamp, nonce, encrypt):
        """用SHA1算法生成安全签名
        @param token:  票据
        @param timestamp: 时间戳
        @param encrypt: 密文
        @param nonce: 随机字符串
        @return: 安全签名
        """
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist).encode())
            return WXBizMsgCrypt_OK, sha.hexdigest()
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e)
            return WXBizMsgCrypt_ComputeSignature_Error, None


class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""

    # xml消息模板
    AES_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signaturet)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>"""

    def extract(self, xmltext):
        """提取出xml数据包中的加密消息
        @param xmltext: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find("Encrypt")
            return WXBizMsgCrypt_OK, encrypt.text
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e)
            return WXBizMsgCrypt_ParseXml_Error, None, None

    def generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        resp_dict = {
            "msg_encrypt": encrypt,
            "msg_signaturet": signature,
            "timestamp": timestamp,
            "nonce": nonce,
        }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml


class PKCS7Encoder:
    """提供基于PKCS7算法的加解密接口"""

    block_size = 32

    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + (pad * amount_to_pad).encode()

    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


class Prpcrypt(object):
    """提供接收和推送给企业微信消息的加解密接口"""

    def __init__(self, key):

        # self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC

    def encrypt(self, text, receiveid):
        """对明文进行加密
        @param text: 需要加密的明文
        @return: 加密得到的字符串
        """
        # 16位随机字符串添加到明文开头
        text = text.encode()
        text = (
            self.get_random_str()
            + struct.pack("I", socket.htonl(len(text)))
            + text
            + receiveid.encode()
        )

        # 使用自定义的填充方式对明文进行补位填充
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        # 加密
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        try:
            ciphertext = cryptor.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return WXBizMsgCrypt_OK, base64.b64encode(ciphertext)
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e)
            return WXBizMsgCrypt_EncryptAES_Error, None

    def decrypt(self, text, receiveid):
        """对解密后的明文进行补位删除
        @param text: 密文
        @return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e)
            return WXBizMsgCrypt_DecryptAES_Error, None
        try:
            pad = plain_text[-1]
            # 去掉补位字符串
            # pkcs7 = PKCS7Encoder()
            # plain_text = pkcs7.encode(plain_text)
            # 去除16位随机字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I", content[:4])[0])
            xml_content = content[4 : xml_len + 4]
            from_receiveid = content[xml_len + 4 :]
        except Exception as e:
            logger = logging.getLogger()
            logger.error(e)
            return WXBizMsgCrypt_IllegalBuffer, None

        if from_receiveid.decode("utf8") != receiveid:
            return WXBizMsgCrypt_ValidateCorpid_Error, None
        return 0, xml_content

    def get_random_str(self):
        """ 随机生成16位字符串
        @return: 16位字符串
        """
        return str(random.randint(1000000000000000, 9999999999999999)).encode()


class WecomApiToolsSecurity(models.Model):
    _name = "wecomapi.tools.security"
    _description = "Wecom API Tools - Security"

    aes_key = fields.Text(string="AES key", readonly=True)
    token = fields.Char(string="token", readonly=True)
    receive_id = fields.Char(string="Receive Id", readonly=True)

    def InitMsgCrypt(self, sToken, sEncodingAESKey, sReceiveId):
        """
        初始化消息加解密对象
        :return:
        """
        msg_crypt = self.search(
            [("token", "=", sToken), ("receive_id", "=", sReceiveId),], limit=1,
        )
        # aes_key = base64.b64decode(sEncodingAESKey + "=")
        aes_key = werkzeug.urls.url_decode(sEncodingAESKey + "=")
        print(aes_key)
        assert len(aes_key) == 32
        if not msg_crypt:
            try:
                msg_crypt = self.sudo().create(
                    {"aes_key": str(aes_key, encoding="utf8")}
                )
            except Exception as e:
                pass
                # throw_exception("[error]: EncodingAESKey unvalid !", FormatException)
            else:
                msg_crypt.sudo().write(
                    {"token": sToken, "receive_id": sReceiveId,}
                )
        else:
            msg_crypt.sudo().write(
                {
                    "aes_key": str(aes_key, encoding="utf8"),
                    "token": sToken,
                    "receive_id": sReceiveId,
                }
            )
        return msg_crypt

        # try:
        #     self.key = base64.b64decode(sEncodingAESKey + "=")
        #     assert len(self.key) == 32
        # except:
        #     pass
        #     # throw_exception("[error]: EncodingAESKey unvalid !", FormatException)
        #     # return ierror.WXBizMsgCrypt_IllegalAesKey,None
        # else:
        #     self.token = sToken
        #     self.receive_id = sReceiveId
        #     return self

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        """验证URL
        @param sMsgSignature: 签名串，对应URL参数的msg_signature
        @param sTimeStamp: 时间戳，对应URL参数的timestamp
        @param sNonce: 随机串，对应URL参数的nonce
        @param sEchoStr: 随机串，对应URL参数的echostr
        @param sReplyEchoStr: 解密之后的echostr，当return返回0时有效
        @return：成功0，失败返回对应的错误码
        """
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, sEchoStr)
        if ret != 0:
            return ret, None
        if not signature == sMsgSignature:
            return WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.aes_key)
        ret, sReplyEchoStr = pc.decrypt(sEchoStr, self.receive_id)
        return ret, sReplyEchoStr

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp=None):
        """将企业回复用户的消息加密打包
        @param sReplyMsg: 企业号待回复用户的消息，xml格式的字符串
        @param sTimeStamp: 时间戳，可以自己生成，也可以用URL参数的timestamp,如为None则自动用当前时间
        @param sNonce: 随机串，可以自己生成，也可以用URL参数的nonce
        sEncryptMsg: 加密后的可以直接回复用户的密文，包括msg_signature, timestamp, nonce, encrypt的xml格式的字符串,
        return：成功0，sEncryptMsg,失败返回对应的错误码None
        """

        pc = Prpcrypt(self.aes_key)
        ret, encrypt = pc.encrypt(sReplyMsg, self.receive_id)
        encrypt = encrypt.decode("utf8")
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        # 生成安全签名
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, timestamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        xmlParse = XMLParse()
        return ret, xmlParse.generate(encrypt, signature, timestamp, sNonce)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        """检验消息的真实性，并且获取解密后的明文
        @param sMsgSignature: 签名串，对应URL参数的msg_signature
        @param sTimeStamp: 时间戳，对应URL参数的timestamp
        @param sNonce: 随机串，对应URL参数的nonce
        @param sPostData: 密文，对应POST请求的数据
            xml_content: 解密后的原文，当return返回0时有效
         @return: 成功0，失败返回对应的错误码
        验证安全签名
        """
        xmlParse = XMLParse()
        ret, encrypt = xmlParse.extract(sPostData)
        if ret != 0:
            return ret, None
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        if not signature == sMsgSignature:
            return WXBizMsgCrypt_ValidateSignature_Error, None
        pc = Prpcrypt(self.aes_key)
        ret, xml_content = pc.decrypt(encrypt, self.receive_id)
        return ret, xml_content

    def generate_jsapi_signature(self, company, nonceStr, timestamp, url):
        """
        使用sha1加密算法，生成JSAPI的签名
        ------------------------------
        company: 公司
        nonceStr: 生成签名的随机串
        timestamp: 生成签名的时间戳
        url: 当前网页的URL， 不包含#及其后面部分
        """

        # 生成签名前，刷新 ticke  .search([(("is_wecom_organization", "=", True))])
        # company.sudo().get_jsapi_ticket()

        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        ticket = company.corp_jsapi_ticket

        str = ("jsapi_ticket=%s&noncestr=%s&timestamp=%s&url=%s") % (
            ticket,
            nonceStr,
            timestamp,
            url,
        )
        encrypts = hashlib.sha1(str.encode("utf-8")).hexdigest()
        return encrypts

