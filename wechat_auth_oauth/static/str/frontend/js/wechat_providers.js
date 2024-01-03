odoo.define('wechat_auth_oauth.providers', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;


    publicWidget.registry.WechatAuthProviders = publicWidget.Widget.extend({
        selector: 'div.o_login_auth',
        // xmlDependencies: ['/wecom_auth_oauth/static/src/xml/providers.xml'],
        events: {
            'click a': '_onClick',
        },
        jsLibs: [
            document.location.protocol + "res.wx.qq.com/connect/zh_CN/htmledition/js/wxLogin.js",
        ],
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.is_wechat_browser = self.is_wechat_browser();
            this.wechat_login_info = self._rpc({
                route: "/get_wechat_login_info",
                params: {
                    is_wechat_browser: self.is_wechat_browser,
                },
            });
            console.log("微信验证方式信息", this.wechat_login_info)
            this.showOrHideWecomProvider();
            if (document.readyState == "complete") {
                // 页面载入完成，显示 "o_login_auth" 元素
                this.$el.removeClass("o_hidden");
            }
            return this._super.apply(this, arguments);
        },
        showOrHideWecomProvider: function () {
            let self = this;
            let $oauth_providers = this.$el.find("a");

            _.forEach($oauth_providers, function (provider) {
                let $provider = $(provider);
                let url = $provider.attr("href");
                if (url.indexOf("open.weixin.qq.com/connect/oauth2/authorize") >= 0) {
                    if (self.is_wecom_browser) {
                        $provider.removeClass("o_hidden").addClass("border rounded");
                    } else {
                        $provider.addClass("o_hidden");
                    }
                } else if (url.indexOf("open.work.weixin.qq.com/wwopen/sso/qrConnec") >= 0) {
                    if (!self.is_wecom_browser) {
                        $provider.removeClass("o_hidden").addClass("border rounded");
                    } else {
                        $provider.addClass("o_hidden");
                    }
                }
            });
        },
        is_wechat_browser: function () {
            var ua = navigator.userAgent.toLowerCase();
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                return false;
            } else {
                return true;
            }
        },
        is_wecom_browser: function () {
            var ua = navigator.userAgent.toLowerCase();
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                return false;
            } else {
                let isWxWork = ua.match(/WxWork/i) == "wxwork";
                if (isWxWork) {
                    return true;
                } else {
                    return false;
                }
            }
        },
        is_ios: function () {
            var isIphoneOrIpad = /iphone|ipad/i.test(navigator.userAgent);
            if (isIphoneOrIpad) {
                return true;
            } else {
                return false;
            }
        },
        _onClick: async function (ev) {
            ev.preventDefault(); //阻止默认行为
            console.log($(ev.target));
            var self = this;
            var url = $(ev.target).attr('href');
            var icon = $(ev.target).find("i")

            // const data = await Promise.resolve(self.companies);
            // if ($(ev.target).prop("tagName") == "I") {
            //     url = $(ev.target).parent().attr('href');
            //     icon = $(ev.target);
            // }


        },
        updateUrlParam: function (url, name, new_value) {
            var self = this;

            if (url.indexOf(name + '=') > 0) {
                // url有参数名，进行修改
                var original_value = self.getUrlParam(url, name);
                if (original_value != "") {
                    //url包含参数值
                    url = url.replace(name + '=' + original_value, name + '=' + new_value)
                } else {
                    //url不包含参数值
                    url = url.replace(name + '=', name + '=' + new_value)
                }

            } else {
                // url无参数名，进行添加
                if (url.indexOf("?") > 0) {
                    url = url + "&" + name + "=" + new_value;
                } else {
                    url = url + "?" + name + "=" + new_value;
                }
            }
            return url;
        },
        getUrlParam: function (url, paraName) {
            var arrObj = url.split("?");
            if (arrObj.length > 1) {
                var arrPara = arrObj[1].split("&");
                var arr;
                for (var i = 0; i < arrPara.length; i++) {
                    arr = arrPara[i].split("=");
                    if (arr != null && arr[0] == paraName) {
                        return arr[1];
                    }
                }
                return "";
            } else {
                return "";
            }
        },
        generateNonceStr: function (len) {
            //生成签名的随机串
            len = len || 32;
            var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'; // 默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1
            var maxPos = $chars.length;
            var str = '';
            for (var i = 0; i < len; i++) {
                str += $chars.charAt(Math.floor(Math.random() * maxPos));
            }
            return str;
        },
    });
});