import Helper from "@ember/component/helper";

/**
* @method gettextHelper
* @description: Helper for get function gettext of django for i18n
* @param {*} msgid
*/
export function gettextHelper(msgid) {
    if(typeof(window.django) === "undefined") {
      return msgid;
    } else {
      return window.django.gettext(msgid);
    }
}

export default Helper.helper(gettextHelper);
