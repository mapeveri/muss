import Component from '@ember/component';

export default Component.extend({
    typeNotificationTopic: false,
    typeNotificationComment: false,
    typeNotificationRegister: false,

    didInsertElement() {
        this._super();

        //Get type notification
        if (Object.keys(this.get('notification.topic')).length > 0) {
            this.set('typeNotificationTopic', true);
        } else if(Object.keys(this.get('notification.comment')).length > 0) {
            this.set('typeNotificationComment', true);
        } else {
            this.set('typeNotificationRegister', true);
        }
    }
});
