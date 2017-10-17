import Controller from "@ember/controller";
import { inject as service} from '@ember/service';
import { schedule } from "@ember/runloop"
import $ from 'jquery';
import config from './../config/environment';
import { getUrlConnectionWs } from '../libs/utils';

export default Controller.extend({
    ajax: service('ajax'),
    session: service('session'),
    store: service('store'),
    currentUser: service('current-user'),
    totalWsNotifications: 0,

    init() {
        this._super();

        schedule('afterRender', () => {
            setTimeout(() => {
                $('.ui.dropdown').dropdown();
            }, 1000);
        });

        //Connect to ws for notifications
        this.webSocketNotifications();
    },
    /**
    * @method webSocketNotifications
    * @description: Get notifications from ws
    */
    webSocketNotifications() {
        let urlWs = getUrlConnectionWs();
        let url = urlWs + "notification?user=" + this.get('currentUser').user.id;
        let ws = new WebSocket(url);
        ws.onmessage = (evt) => {
            let json = evt.data;
            let obj = JSON.parse(json);

            //Set notifications
            let totalModelNotification = this.get('model.totalNotifications').total;
            if(totalModelNotification > this.totalWsNotifications) {
                this.totalWsNotifications = totalModelNotification;
            }

            //Show notification
            this.totalWsNotifications += 1;
            $("#total_notifications").removeClass("hide");
            $("#total_notifications").text(this.totalWsNotifications);

            //Add record
            let record = this.get('store').createRecord('notification', {
                topic: obj.topic,
                comment: obj.comment,
                isSeen: false,
                date: new Date()
            });
            this.get('model.notifications').unshiftObject(record._internalModel);
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
                $("#total_notifications").addClass("hide");
            });
        }
    }
});
