/** @odoo-module */

import publicWidget from "web.public.widget";
import "portal.portal"; // force dependencies

publicWidget.registry.PortalHomeCounters.include({
  start: function () {
    var def = this._super.apply(this, arguments);
    this._setCareModel();
    return def;
  },
  _setCareModel:function(){
    var careModel = window.localStorage.getItem("care_mode");
    console.log("当前关爱模式",careModel);
    console.log("当前el",this.$el);
  },
});
