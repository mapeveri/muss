import Controller from "@ember/controller";
import { inject as service} from '@ember/service';
import { schedule } from "@ember/runloop"
import $ from 'jquery';

export default Controller.extend({
    session: service('session'),
    init() {
        this._super();

        schedule('afterRender', () => {
            setTimeout(() => {
                $('.ui.dropdown').dropdown();
            }, 1000);
        });
    },
    actions: {
        /**
        * @method invalidateSession
        * @description: Logout
        */
        invalidateSession() {
            this.get('session').invalidate();
        },
        /**
        * @method onSearch
        * @description: Event onkeyup input search
        * @param {*} q
        */
        onSearch(q) {
            this.transitionToRoute('search-topic', { queryParams: { q: q } });
        },
        openNotifications() {
            //
        }
    }
});
