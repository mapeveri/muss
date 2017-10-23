import Component from '@ember/component';
import { setTitlePage } from '../libs/utils';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    didInsertElement() {
        this._super();

        //Update title page html
        setTitlePage(window.muss.site_name + " - " + gettextHelper("Find Topics"));
    }
});
