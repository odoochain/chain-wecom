odoo.define('wecom_auth_oauth.providers', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;


    publicWidget.registry.WecomAuthProviders = publicWidget.Widget.extend({
        selector: 'div.o_login_auth',
        xmlDependencies: ['/wecom_auth_oauth/static/src/xml/providers.xml'],
        events: {
            'click a': '_onClick',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.companies = self._rpc({
                route: "/wxowrk_login_info",
                params: {
                    is_wecom_browser: self.is_wecom_browser()
                },
            });

            const timestamp = new Date().getTime();
            const nonceStr = self.generateNonceStr(16);
            // const url = window.location.pathname; //当前网页的URL， 不包含#及其后面部分
            const url = window.location.href.split("#")[0]; //当前网页的URL， 不包含#及其后面部分
            console.log(document.readyState)
            if (document.readyState == "complete") {
                // 页面载入完成，显示 "o_login_auth" 元素
                this.$el.removeClass("d-none");
            }
            return this._super.apply(this, arguments);
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

            var self = this;
            var url = $(ev.target).attr('href');
            var icon = $(ev.target).find("i")

            const data = await Promise.resolve(self.companies);
            if ($(ev.target).prop("tagName") == "I") {
                url = $(ev.target).parent().attr('href');
                icon = $(ev.target);
            }

            var companies = [];
            if (data["companies"].length > 0) {
                $.each(data["companies"], function (index, element) {
                    var state = self.getUrlParam(url, "state").replace(/[+]/g, "").replace("#wechat_redirect", "");
                    var state_decode_str = decodeURIComponent(state);
                    var new_state = state_decode_str.slice(0, 1) + '"a":' + '"' + element["appid"] + '",' + state_decode_str.slice(1);
                    var state_encode_str = encodeURIComponent(new_state)

                    var new_url = self.updateUrlParam(url, 'state', state_encode_str);
                    new_url = self.updateUrlParam(new_url, 'appid', element["appid"]);
                    new_url = self.updateUrlParam(new_url, 'agentid', element["agentid"]);

                    new_url = new_url + "#wechat_redirect";

                    companies.push({
                        "id": element["id"],
                        "name": element["name"],
                        "url": new_url,
                    });
                });

                if (icon.hasClass("wecom_auth_scancode")) {
                    var dialog = $(qweb.render('wecom_auth_oauth.OauthQrDialog', {
                        companies: companies,
                    }));
                    if (self.$el.parents("body").find("#wecom_qr_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');

                } else if (icon.hasClass("wecom_auth_onekey")) {
                    var new_data = {
                        isWxworkBrowser: data["is_wecom_browser"],
                        msg: data["msg"],
                        companies: companies,
                    };
                    var dialog = $(qweb.render('wecom_auth_oauth.OauthLoginDialog', {
                        data: new_data
                    }));
                    if (self.$el.parents("body").find("#wecom_login_dialog").length == 0) {
                        dialog.appendTo($(document.body));
                    }
                    dialog.modal('show');
                } else {
                    window.open(url);
                }
            } else {
                window.open(url);
            }
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

        // -------------------------------
        // JS-SDK
        // -------------------------------
        // setWxConfig: async function () {
        //     var self = this;
        //     const data = await Promise.resolve(self.wx_configs_data);
        //     var parameters = data[0]["parameters"];
        //     // var FirstWxConfig = new wxconfig(self, {
        //     wx.config({
        //         beta: parameters["beta"],
        //         debug: parameters["debug"],
        //         // debug: false,
        //         appId: parameters["appId"],
        //         timestamp: parameters["timestamp"],
        //         nonceStr: parameters["nonceStr"],
        //         signature: parameters["signature"],
        //         jsApiList: ["getBrandWCPayRequest", "WeixinJSBridge"], //必填，需要使用的JS接口列表，凡是要调用的接口都需要传进来
        //     })
        //     // FirstWxConfig.start()
        //     wx.ready(function () {
        //         function onBridgeReady() {
        //             WeixinJSBridge.invoke();
        //         }
        //         if (typeof WeixinJSBridge == "undefined") {
        //             if (document.addEventListener) {
        //                 document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
        //             } else if (document.attachEvent) {
        //                 document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
        //                 document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
        //             }
        //         } else {
        //             onBridgeReady();
        //         }
        //     });
        //     wx.error(function (res) {
        //         console.log(res)
        //         // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开config的debug模式查看，也可以在返回的res参数中查看，对于SPA可以在这里更新签名。
        //     });

        // },
        // get_jsapi_parameter: async function (nonceStr, timestamp, url, company_id) {
        //     var self = this;
        //     return self._rpc({
        //         route: "/wecom_login_jsapi",
        //         params: {
        //             company_id: company_id,
        //             nonceStr: nonceStr,
        //             timestamp: timestamp,
        //             url: url,
        //         },

        //     }).then(function (response) {
        //         // return response;
        //         return Promise.resolve(response);
        //     })
        // },
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