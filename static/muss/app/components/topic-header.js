import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import ENV from './../config/environment';
import { closeAllEditor, getUrlConnectionWs, setTitlePage, showModalLogin } from '../libs/utils';

export default Component.extend({
    ajax: service('ajax'),
    store: service('store'),
    session: service('session'),
    currentUser: service('current-user'),
    namespace: ENV.APP.API_NAMESPACE,
    currentUrl: window.location.href,
    isLoaded: false,
    topic: null,
    hitTopic: null,
    isCreatorTopic: false,
    isLikeTopicUser: false,
    userLogin: null,
    topicId: null,
    showLike: true,
    totalCommentsWatcher: function() {
        this.set('topic.totalComments', this.get('comments.content').length);
    }.observes('comments.content.[]'),
    editTopicField: '',
    editTopicTitle: '',
    enableEditTopic: function() {
        return !isPresent(this.editTopicField) || !isPresent(this.editTopicTitle);
    }.property('editTopicField', 'editTopicTitle'),
    isTrollUser: false,

    didInsertElement() {
        this._super();

        //Update title page html
        setTitlePage(this.get('topic.title'));

        if (this.get('session.isAuthenticated')) {
            //Check if user logged is the creator of topic
            let user_login = parseInt(this.get('currentUser').user.id);
            this.set('userLogin', user_login);
            let user_topic = this.get('topic.user.id');
            if(user_login == user_topic) {
                this.set('isCreatorTopic', true);
            }

            //Set is the user logged is a troll
            this.set('isTrollUser', this.get('profile.isTroll'));
            //Set topic id
            this.set('topicId', this.get('topic.id'));

            //Check user like in topic
            this.getCheckUserLike();
        }

        //Comment and websockets
        this.connectionCommentToWs();

        //Get or make hit count for topic
        this.getOrMakeHitTopic().then(() => {
            //Is completed
            this.set('isLoaded', true);
        });
    },
    /**
    * @method connectionCommentToWs
    * @description: Connect to ws for get comments in realtime
    */
    connectionCommentToWs() {
        let urlWs = getUrlConnectionWs();
        let url = urlWs + "comment?topic=" + this.get('topic.id');
        let ws = new WebSocket(url);
        ws.onmessage = (evt) => {
            let json = evt.data;
            let obj = JSON.parse(json);

            this.get('store').find('user', obj.comment.userid).then((user) => {
                //Add record
                let record = this.get('store').createRecord('comment', {
                    topic: this.get('topic'),
                    user: user,
                    id: obj.comment.commentId,
                    date: new Date().toLocaleString(),
                    totalLikes: 0,
                    likes: 0,
                    htmlDescription: obj.html_description,
                    description: obj.description,
                    isRealTime: true,
                });

                this.get('comments').pushObject(record._internalModel);
            });
        };

    },
    /**
    * @method getOrMakeHitTopic
    * @description: Get or make hit count for topic
    */
    getOrMakeHitTopic() {
        return this.get('ajax').request('/' + this.namespace + '/hitcounts/', {
            method: 'POST',
            data: {'topic': this.topic.id}
        }).then(response => {
            this.set('hitTopic', response.data.total);
        });
    },

    /**
    * @method getCheckUserLike
    * @description: Check if user logged make like in topic
    */
    getCheckUserLike() {
        let likes = this.get('topic.likes');
        if (likes.length > 0) {
            let exists = likes.find(o => o.user === this.userLogin);
            if(exists != undefined) {
                this.set('showLike', false);
            }
        }
    },
    actions: {
        /**
        * @method likeTopic
        * @description: Save like topic in db
        */
        likeTopic() {
            if(this.get('session.isAuthenticated')) {
                this.get('ajax').request('/' + this.namespace + '/liketopics/', {
                    method: 'POST',
                    data: {
                        'topic': this.topicId,
                        'users': this.userLogin
                    },
                }).then(() => {
                    this.set('showLike', false);
                    this.set('topic.totalLikes', this.get('topic.totalLikes') + 1);
                });
            } else {
                showModalLogin();
            }
        },
        /**
        * @method unLikeTopic
        * @description: Delete like topic in db
        */
        unLikeTopic() {
            this.get('ajax').request('/' + this.namespace + '/liketopics/' + this.topicId + '/', {
                method: 'DELETE',
                data: {
                    'users': this.userLogin
                },
            }).then(() => {
                this.set('showLike', true);
                this.set('topic.totalLikes', this.get('topic.totalLikes') - 1);
            });
        },
        /**
        * @method confirmRemoveTopic
        * @description: Display modal for confirm remove topic
        * @param {*} id
        */
        confirmRemoveTopic(id) {
            $('.tiny.topic_'+id+'.modal').modal({
                onApprove: () => {
                  return false;
                }
            }).modal('show');
        },
        /**
        * @method removeTopic
        * @description: Remove the topic in db
        */
        removeTopic() {
            let id = this.get('topic.id');
            let forum_id = this.get('topic.forum.id');
            let forum_slug = this.get('topic.forum.slug');

            $('.tiny.topic_'+id+'.modal').modal('hide');

            this.topic.destroyRecord().then(() => {
                this.sendAction('redirectForum', forum_id, forum_slug);
            });
        },
        /**
        * @method openTopic
        * @description: Open topic in db
        */
        openTopic() {
            this.topic.set('isClose', false);
            this.topic.save();
        },
        /**
        * @method closeTopic
        * @description: Close topic in db
        */
        closeTopic() {
            this.topic.set('isClose', true);
            this.topic.save();
        },
        /**
        * @method replyTopic
        * @description: Go to reply form
        */
        replyTopic() {
            if(this.get('session.isAuthenticated')) {
                //If exists other editor mde opened, when close all
                closeAllEditor();
                //Show modal editor
                $("#mdeReplyModal").addClass('mde-modal-content-open').height(300).trigger("open");
            } else {
                showModalLogin();
            }
        },
        /**
        * @method showEditTopic
        * @description: Show modal editor mde for edit topic
        */
        showEditTopic() {
            //If exists other editor mde opened, when close all
            closeAllEditor();
            this.set('editTopicTitle', this.get('topic.title'));
            this.set('editTopicField', this.get('topic.description'));
            //Show modal editor
            $("#mdeEditTopicModal").addClass('mde-modal-content-open').height(350).trigger("open");
        },
        /**
        * @method editTopic
        * @description: Update topic in db
        */
        editTopic() {
            this.topic.set('title', this.editTopicTitle);
            this.topic.set('description', this.editTopicField);
            this.topic.save().then(() => {
                //Close editor
                closeAllEditor();
            });
        }
    }
});
