import Ember from 'ember';
import { gettextHelper } from '../helpers/gettext';

export default Ember.Component.extend({
    session: Ember.inject.service('session'),
    store: Ember.inject.service('store'),
    topic: null,
    enableReply: function() {
        return !Ember.isPresent(this.reply);
    }.property('reply'),

    actions: {
        /**
        * @method createComment
        * @description: Create new comment in topic
        */
        createComment() {
            let reply = this.get('reply');
            let user_id = this.get('session').session.content.authenticated.user.id;

            this.get('store').find('user', user_id).then((user) => {
                let comment = this.get('store').createRecord('comment', {
                    'description': reply,
                    'topic': this.topic,
                    'user': user,
                });

                comment.save().then((record) => {
                    this.get('comments.content').pushObject(record._internalModel);
                    this.set('reply', '');
                }).catch(() => {
                    window.toastr.error(gettextHelper("There was an error creating your comment."))
                });
            });
        }
    }
});
