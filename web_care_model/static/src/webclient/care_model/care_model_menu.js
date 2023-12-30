/** @odoo-module **/
import { browser } from '@web/core/browser/browser';
import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { session } from '@web/session';
import { _t } from 'web.core';

const { onMounted, useState, Component } = owl;

export class CareModelMenu extends Component {
    setup() {
        super.setup();


        super.setup();
        this.state = useState({
            careModel: window.localStorage.getItem("care_mode"),
        });

        onMounted(() => this._mounted());
    }

    _mounted() {
        this.navbar = this.__owl__.parent.parent;
        this.header = this.navbar.bdom.el;
        this.body = this.navbar.bdom.parentEl;
        // this.main = this.body.querySelector(".o_action_manager");
        // console.log("----------------header", this.header);
        // console.log("----------------body", this.body);
        // console.log("----------------main", this.main);
        // config.device.isMobileDevice &&
        if (this.state.careModel) {
            this.body.classList.add('o_web_client_card_model');
        } else {
            this.body.classList.remove('o_web_client_card_model');
        }
    }

    onToggle() {
        this.state.careModel = !this.state.careModel;
        window.localStorage.setItem("care_mode", this.state.careModel);
        if (this.state.careModel) {
            this.body.classList.add('o_web_client_card_model');
        } else {
            this.body.classList.remove('o_web_client_card_model');
        }
    }
}

CareModelMenu.template = 'web.CareModelMenu';

export const systrayItem = {
    Component: CareModelMenu,
    isDisplayed(env) {
        return true;
        // const disable_customization = session.theme.disable_customization;
        // return !disable_customization;
    }
};

registry.category('systray').add('CareModelMenu', systrayItem, {
    sequence: 500
});
