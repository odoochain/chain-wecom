/** @odoo-module */

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';
import { listView } from '@web/views/list/list_view';
import { ListController } from '@web/views/list/list_controller';
import { _t } from 'web.core';


export class WechatMessageTemplateListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService('orm');
		this.action = useService('action');
    }

    async onClickGetWechatMessageTemplateList() {
        const result = await this.orm.call('wechat.message_template_list', 'get_wechat_message_template_list', []);
        if (result['state']) {
            this.action.doAction({
				type: 'ir.actions.client',
				tag: 'display_notification',
				params: {
					type: 'success',
					title: _t('Get successfully!'),
					message: result['msg'],
					sticky: false,
					next: {
						type: 'ir.actions.client',
						tag: 'reload'
					}
				}
			});
        }
        else {
            this.action.doAction({
				type: 'ir.actions.client',
				tag: 'display_notification',
				params: {
					type: 'danger',
					title: _t('Get failed!'),
					message: result['msg'],
					sticky: true
				}
			});
        }
    }
}

registry.category('views').add('wechat_message_template_list', {
    ...listView,
    Controller: WechatMessageTemplateListController,
    buttonTemplate: 'WechatMessageTemplateListView.buttons'
});
