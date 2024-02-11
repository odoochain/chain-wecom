# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import logging
import hashlib
import random
import hashlib
from Crypto.Cipher import AES
from passlib.context import CryptContext
import xml.etree.cElementTree as ET
import hashlib


_logger = logging.getLogger(__name__)

NUMLIST = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "q",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "W",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


class WeChatApiToolsSecurity(models.AbstractModel):
    _name = "wechat.tools.security"
    _description = "Wechat API Tools - Security"

    def random_str(self, num):
        """
        生成随机字符串
        :return:
        """
        rang = num
        if rang == None:
            random_str = "".join(random.choice(NUMLIST) for i in range(8))
        else:
            random_str = "".join(random.choice(NUMLIST) for i in range(int(rang)))
        return random_str

    def random_passwd(self, num):
        """
        生成随机密码
        :return:
        """
        rang = num
        if rang == None:
            passwd = "".join(random.choice(NUMLIST) for i in range(8))
        else:
            passwd = "".join(random.choice(NUMLIST) for i in range(int(rang)))

        crypt_context = CryptContext(
            schemes=["pbkdf2_sha512", "plaintext"], deprecated=["plaintext"]
        )
        hash_password = (
            crypt_context.hash
            if hasattr(crypt_context, "hash")
            else crypt_context.encrypt
        )
        return hash_password(passwd)
