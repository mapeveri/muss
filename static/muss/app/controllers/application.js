import Controller from "@ember/controller";
import { inject as service} from '@ember/service';
import { schedule } from "@ember/runloop"
import $ from 'jquery';
import config from './../config/environment';
import { getUrlConnectionWs } from '../libs/utils';

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

        let urlWs = getUrlConnectionWs();
        let url = urlWs + "notification?user=" + this.get('currentUser').user.id;
        let ws = new WebSocket(url);
        ws.onmessage = (evt) => {
            let json = evt.data;
            let obj = JSON.parse(json);
            //this.get('model.notifications').addObjects(obj);
        };
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
                $("#total_notifications").hide();
            });
        }
    }
});
