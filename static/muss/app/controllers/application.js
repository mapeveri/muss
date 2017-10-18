import Controller from "@ember/controller";
import { inject as service} from '@ember/service';
import { schedule } from "@ember/runloop"
import $ from 'jquery';
import config from './../config/environment';

export default Controller.extend({
    ajax: service('ajax'),
    session: service('session'),
    currentUser: service('current-user'),

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
        /**
        * @method setSeenNotifications
        * @description: Update notifications seen
        */
        setSeenNotifications() {
            let namespace = config.APP.API_NAMESPACE;
            let user_id = parseInt(this.get('currentUser').user.id);
            let csrftoken = $("[name=csrfmiddlewaretoken]").first().val();
            return this.get('ajax').request('/' + namespace + '/update-seen-notifications-user/', {
                method: 'POST',
                data: {
                    user_id: user_id,
                    csrfmiddlewaretoken: csrftoken,
                }
            }).then(() => {
                $("#total_notifications").addClass("hide");
            });
        }
    }
});
