odoo.define('wecom_auth_oauth.join', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var qweb = core.qweb;

    publicWidget.registry.WxWorkAuthJoin = publicWidget.Widget.extend({
        selector: 'form.oe_login_form',
        // xmlDependencies: ['/wecom_auth_oauth/static/src/xml/join.xml'],

        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            this.companies = self._rpc({
                route: "/wxowrk_login_info",
                params: {

                },
            });

            return this._super.apply(this, arguments).then(this._renderJoin.bind(this));
        },
        _renderJoin: async function () {
            var self = this;
            const data = await Promise.resolve(self.companies);
            var companies = [];
            if (data["companies"].length > 0) {
                $.each(data["companies"], function (index, element) {
                    companies.push({
                        "id": element["id"],
                        "name": element["name"],
                        "url": element["join_qrcode"],
                        "enabled": element["enabled_join"],
                    });
                });

                let show_join = false;
                $.each(companies, function (index, element) {
                    if (element["enabled"]) {
                        show_join = true;
                    }
                });

                if (show_join) {
                    var $auth_element = self.$el.find(".o_login_auth");
                    var $join_element = $(qweb.render('wecom_auth_oauth.Join', {
                        button_name: data["join_button_name"],
                        // enabled: companies,
                        companies: companies,
                    }));
                    $auth_element.before($join_element);
                }
            }
        },
    })
});