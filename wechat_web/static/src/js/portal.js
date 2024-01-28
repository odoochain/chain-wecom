odoo.define('wechat_web.portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const { _t, qweb } = require('web.core');
    const session = require('web.session');


    publicWidget.registry.WechatPortalHomeCounters = publicWidget.Widget.extend({
        selector: '.o_wechat_portal_home',

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            this._updateCounters();
            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * Return a list of counters name linked to a line that we want to keep
         * regardless of the number of documents present
         * @private
         * @returns {Array}
         */
        _getCountersAlwaysDisplayed() {
            return [];
        },

        /**
         * @private
         */
        async _updateCounters(elem) {
            const numberRpc = 3;
            const needed = Object.values(this.el.querySelectorAll('[data-placeholder_count]'))
                .map(documentsCounterEl => documentsCounterEl.dataset['placeholder_count']);
            const counterByRpc = Math.ceil(needed.length / numberRpc);  // max counter, last can be less
            const countersAlwaysDisplayed = this._getCountersAlwaysDisplayed();

            const proms = [...Array(Math.min(numberRpc, needed.length)).keys()].map(async i => {
                const documentsCountersData = await this._rpc({
                    route: "/wechat/web/counters",
                    params: {
                        counters: needed.slice(i * counterByRpc, (i + 1) * counterByRpc)
                    },
                });

                Object.keys(documentsCountersData).forEach(counterName => {
                    const documentsCounterEl = this.el.querySelector(`[data-placeholder_count='${counterName}']`);
                    documentsCounterEl.textContent = documentsCountersData[counterName];
                    // The element is hidden by default, only show it if its counter is > 0 or if it's in the list of counters always shown
                    //默认情况下，该元素处于隐藏状态，仅当其计数器> 0 或始终显示在计数器列表中时才显示该元素
                    if (documentsCountersData[counterName] !== 0 || countersAlwaysDisplayed.includes(counterName)) {
                        documentsCounterEl.parentElement.classList.remove('d-none');
                    }
                });
                return documentsCountersData;
            });
            return Promise.all(proms).then((results) => {
                const counters = results.reduce((prev, current) => Object.assign({ ...prev, ...current }), {});

                const spinner = this.el.querySelector('.o_portal_doc_spinner')
                if (spinner !== null) {
                    this.el.querySelector('.o_portal_doc_spinner').remove();
                }
                // Display a message when there are no documents available if there are no counters > 0 and no counters always shown
                // 如果没有> 0 的计数器且始终没有显示计数器，则在没有可用文档时显示消息
                if (!countersAlwaysDisplayed.length && !Object.values(counters).filter((val) => val > 0).length) {
                    const no_doc_message = this.el.querySelector('.o_portal_no_doc_message');
                    if (spinner !== null) {
                        this.el.querySelector('.o_portal_no_doc_message').classList.remove('d-none');
                    }
                }
            });
        },
    });

});
