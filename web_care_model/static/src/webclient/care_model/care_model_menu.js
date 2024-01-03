/** @odoo-module **/
import { browser } from '@web/core/browser/browser';
import { useService } from '@web/core/utils/hooks';
import { registry } from '@web/core/registry';
import { session } from '@web/session';
import { _t } from 'web.core';

const { onWillStart, onMounted, useState, Component } = owl;

export class CareModelMenu extends Component {
    setup() {
        super.setup();


        super.setup();
        this.state = useState({
            careModel: false,
        });

        onMounted(() => this._mounted());
        onWillStart(async () => {
            await this.initCareModel();
        });
    }

    async initCareModel() {
        this.state.careModel = window.localStorage.getItem("care_mode");
    }

    _mounted() {
        this.navbar = this.__owl__.parent.parent;
        this.header = this.navbar.bdom.el;
        this.body = this.navbar.bdom.parentEl;

        if (this.state.careModel === "true") {
            console.log("是关爱模式");
            this.body.classList.add('o_web_client_card_model');
            this.state.careModel = true;
        } else {
            console.log("非关爱模式");
            this.body.classList.remove('o_web_client_card_model');
            this.state.careModel = false;
        }
    }

    onToggle() {
        this.state.careModel = !this.state.careModel;

        if (this.state.careModel) {
            this.body.classList.add('o_web_client_card_model');
        } else {
            this.body.classList.remove('o_web_client_card_model');
        }

        window.localStorage.setItem("care_mode", this.state.careModel);
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
