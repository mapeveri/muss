import Component from '@ember/component';
import { setTitlePage } from '../libs/utils';

export default Component.extend({
    didInsertElement() {
        this._super();

        //Update title page html
        setTitlePage(window.muss.site_name);
    }
});
