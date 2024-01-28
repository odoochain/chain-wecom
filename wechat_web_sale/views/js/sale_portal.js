/** @odoo-module */

import publicWidget from 'web.public.widget';
import "wechat_web.portal"; // force dependencies

publicWidget.registry.WechatPortalHomeCounters.include({
    /**
     * @override
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['quotation_count', 'order_count']);
    },
});
