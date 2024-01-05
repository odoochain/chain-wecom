odoo.define('wechat_auth_oauth.login', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;

    publicWidget.registry.WechatAuthLogin = publicWidget.Widget.extend({
        selector: '.o_login_auth',
        xmlDependencies: ['/wechat_auth_oauth/static/src/legacy/public/xml/wechat_providers.xml'],
        events: {
            'click a': '_onClick',
        },
        jsLibs: [
            document.location.protocol + "//res.wx.qq.com/connect/zh_CN/htmledition/js/wxLogin.js",
        ],
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.is_wechat_browser = self.is_wechat_browser();
            this.wechat_provider_info = self._rpc({
                route: "/get_provider_wechat",
                params: {
                    is_wechat_browser: self.is_wechat_browser,
                },
            }).then(function (res) {
                self.wechat_provider_info = res;
                self.initWechatProvider();
            });

            if (document.readyState == "complete") {
                // 页面载入完成，显示 "o_login_auth" 元素
                this.$el.removeClass("o_hidden");
            }

            return this._super.apply(this, arguments);
        },
        initWechatProvider: function () {
            let self = this;
            let $oauth_providers = this.$el.find("a");
            console.log("微信验证方式信息", self.wechat_provider_info);
            _.forEach($oauth_providers, function (provider) {
                let $provider = $(provider);
                let url = $provider.attr("href");
                if (url.indexOf("https://open.weixin.qq.com/connect/qrconnect") >= 0) {
                    // if (self.is_wechat_browser) {
                    //     $provider.removeClass("o_hidden").addClass("border rounded");
                    // } else {
                    //     $provider.addClass("o_hidden");
                    // }
                    if (self.wechat_provider_info["qrcode_display_method"] === "embedded") {
                        $provider.removeClass("o_hidden");
                        $provider.addClass("d-flex justify-content-center");
                        $provider.attr("id", "wechat_qrcode_container");
                        const provider = self.wechat_provider_info;
                        var obj = new WxLogin({
                            self_redirect: false, // true：手机点击确认登录后可以在 iframe 内跳转到 redirect_uri，false：手机点击确认登录后可以在 top window 跳转到 redirect_uri。默认为 false
                            id: "wechat_qrcode_container", // 第三方页面显示二维码的容器id
                            appid: provider["appid"], // 应用唯一标识，在微信开放平台提交应用审核通过后获得
                            scope: provider["scope"], // 应用授权作用域，拥有多个作用域用逗号（,）分隔，网页应用目前仅填写snsapi_login即可
                            redirect_uri: provider["redirect_uri"], // 重定向地址，需要进行UrlEncode
                            state: provider["state"], // 用于保持请求和回调的状态，授权请求后原样带回给第三方。该参数可用于防止csrf攻击（跨站请求伪造攻击），建议第三方带上该参数，可设置为简单的随机数加session进行校验
                            style: provider["style"], // 提供"black"、"white"可选，默认为黑色文字描述。
                            href: provider["href"]// 自定义样式链接，第三方可根据实际需求覆盖默认样式。
                        });

                    } else {
                        $provider.removeClass("o_hidden")
                    }


                }
            });
        },
        initWecharQRCodeContainer() { },
        is_wechat_browser: function () {
            var ua = navigator.userAgent.toLowerCase();
            let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
            if (!isWx) {
                return false;
            } else {
                return true;
            }
        },
        // is_wecom_browser: function () {
        //     var ua = navigator.userAgent.toLowerCase();
        //     let isWx = ua.match(/MicroMessenger/i) == "micromessenger";
        //     if (!isWx) {
        //         return false;
        //     } else {
        //         let isWxWork = ua.match(/WxWork/i) == "wxwork";
        //         if (isWxWork) {
        //             return true;
        //         } else {
        //             return false;
        //         }
        //     }
        // },
        // is_ios: function () {
        //     var isIphoneOrIpad = /iphone|ipad/i.test(navigator.userAgent);
        //     if (isIphoneOrIpad) {
        //         return true;
        //     } else {
        //         return false;
        //     }
        // },
        _onClick: async function (ev) {
            ev.preventDefault(); //阻止默认行为

            const self = this;
            let auth_url = $(ev.target).attr('href');
            let icon = $(ev.target).find("i")

            if ($(ev.target).prop("tagName") == "I") {
                auth_url = $(ev.target).parent().attr('href');
                icon = $(ev.target);
            }

            if (auth_url.indexOf("https://open.weixin.qq.com/connect/qrconnect") >= 0) {
                var dialog = $(qweb.render('wechat_auth_oauth.QrCodeDialog', {
                    url: auth_url
                }));
                if (self.$el.parents("body").find("#wechat_qr_dialog").length == 0) {
                    dialog.appendTo($(document.body));
                }
                dialog.modal('show');
            } else {
                window.open(url);
            }

        },
        // updateUrlParam: function (url, name, new_value) {
        //     var self = this;

        //     if (url.indexOf(name + '=') > 0) {
        //         // url有参数名，进行修改
        //         var original_value = self.getUrlParam(url, name);
        //         if (original_value != "") {
        //             //url包含参数值
        //             url = url.replace(name + '=' + original_value, name + '=' + new_value)
        //         } else {
        //             //url不包含参数值
        //             url = url.replace(name + '=', name + '=' + new_value)
        //         }

        //     } else {
        //         // url无参数名，进行添加
        //         if (url.indexOf("?") > 0) {
        //             url = url + "&" + name + "=" + new_value;
        //         } else {
        //             url = url + "?" + name + "=" + new_value;
        //         }
        //     }
        //     return url;
        // },
        // getUrlParam: function (url, paraName) {
        //     var arrObj = url.split("?");
        //     if (arrObj.length > 1) {
        //         var arrPara = arrObj[1].split("&");
        //         var arr;
        //         for (var i = 0; i < arrPara.length; i++) {
        //             arr = arrPara[i].split("=");
        //             if (arr != null && arr[0] == paraName) {
        //                 return arr[1];
        //             }
        //         }
        //         return "";
        //     } else {
        //         return "";
        //     }
        // },
        // generateNonceStr: function (len) {
        //     //生成签名的随机串
        //     len = len || 32;
        //     var $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'; // 默认去掉了容易混淆的字符oOLl,9gq,Vv,Uu,I1
        //     var maxPos = $chars.length;
        //     var str = '';
        //     for (var i = 0; i < len; i++) {
        //         str += $chars.charAt(Math.floor(Math.random() * maxPos));
        //     }
        //     return str;
        // },
    });
    return publicWidget.registry.WechatAuthLogin;
});