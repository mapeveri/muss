import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';
import { getUrlConnectionWs, setTitlePage } from '../libs/utils';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    session: service('session'),
    store: service('store'),
    currentUser: service('current-user'),
    totalWsNotifications: 0,
    notifications: [],

    didInsertElement() {
        this._super();

        //Update title page html
        setTitlePage(gettextHelper("Notifications"));

        //If is authenticate, set connection ws for notifications
        if (this.get('session.isAuthenticated')) {
            if(this.get('model.notifications')) {
                this.set('notifications', this.get('model.notifications'));
            } else {
                this.set('notifications', this.get('model'));
            }

            let urlWs = getUrlConnectionWs();
            let url = urlWs + "notification?user=" + this.get('currentUser').user.id;
            let ws = new WebSocket(url);
            ws.onmessage = (evt) => {
                let json = evt.data;
                let obj = JSON.parse(json);

                //Set notifications
                try {
                    let totalModelNotification = this.get('model.totalNotifications').total;
                    if(totalModelNotification > this.totalWsNotifications) {
                        this.totalWsNotifications = totalModelNotification;
                    }

                    //Show notification
                    this.totalWsNotifications += 1;
                    $("#total_notifications").removeClass("hide");
                    $("#total_notifications").text(this.totalWsNotifications);
                } catch(e) {
                    //
                }

                //Add record
                let record = this.get('store').createRecord('notification', {
                    topic: obj.topic,
                    comment: obj.comment,
                    isSeen: false,
                    date: new Date().toLocaleString(),
                });

                try {
                    this.get('model.notifications').unshiftObject(record._internalModel);
                } catch(e) {
                    this.get('model').unshiftObject(record._internalModel);
                }
            };
        }
    }
});
