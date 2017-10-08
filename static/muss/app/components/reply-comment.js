import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    session: service('session'),
    store: service('store'),
    topic: null,
    reply: '',
    enableReply: function() {
        return !isPresent(this.reply);
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

                    setTimeout(() => {
                        //Hide modal editor
                        $("#mdeReplyModal").removeClass('mde-modal-content-open').height(0).trigger("close");
                    }, 100);
                }).catch(() => {
                    window.toastr.error(gettextHelper("There was an error creating your comment."))
                });
            });
        }
    }
});
