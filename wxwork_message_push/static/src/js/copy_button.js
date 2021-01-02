odoo.define('wxwork_message_push.list_copy_button_create', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.o_list_wxwork_copy_email_template', this._copy_email_template.bind(this));
            }
        },
        _copy_email_template: function () {
            // console.log("点击复制")
            var self = this;
            // var records = this.getSelectedIds();
            self._rpc({
                model: 'wxwork.message.template',
                method: 'copy_mail_template',
                args: [],
            }).then(function (res) {
                if (res) {
                    self.displayNotification({
                        type: 'success',
                        title: _t("Copy successfully!"),
                        message: _t("Copy One-click copy of email template succeeded!"),
                        sticky: false,
                        // className: "bg-success",
                        // next: self.trigger_up('reload')
                        next: {
                            "type": "ir.actions.client",
                            "tag": "reload",
                        }
                    });
                    // self.trigger_up('reload');
                }

            });
        }
    });
});