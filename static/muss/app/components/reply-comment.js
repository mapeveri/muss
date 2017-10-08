import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    session: service('session'),
    store: service('store'),
    topic: null,
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

                    //Hide modal reply
                    setTimeout(() => {
                        $("#mdeReplyModal").hide()
                        $("#content-topic").removeClass("paddingEditorMde");
                    }, 100);
                }).catch(() => {
                    window.toastr.error(gettextHelper("There was an error creating your comment."))
                });
            });
        }
    }
});
