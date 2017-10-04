import Ember from 'ember';
import ENV from './../config/environment';
import { showModalLogin } from '../libs/utils';

export default Ember.Component.extend({
    ajax: Ember.inject.service(),
    session: Ember.inject.service('session'),
    router: Ember.inject.service('-routing'),
    currentUser: Ember.inject.service('current-user'),
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
    jwt: null,
    totalCommentsWatcher: function() {
        this.set('topic.totalComments', this.get('comments.content').length);
    }.observes('comments.content.[]'),

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            //Check if user logged is the creator of topic
            let user_login = parseInt(this.get('currentUser').user.id);
            this.set('userLogin', user_login);
            let user_topic = this.get('topic.user.id');
            if(user_login == user_topic) {
                this.set('isCreatorTopic', true);
            }

            this.set('topicId', this.get('topic.id'));
            this.set('jwt', this.get('session').session.content.authenticated.token);

            //Check user like in topic
            this.getCheckUserLike();
        }

        //Get or make hit count for topic
        this.getOrMakeHitTopic();
    },

    /**
    * @method: getOrMakeHitTopic
    * @description: Get or make hit count for topic
    */
    getOrMakeHitTopic() {
        return this.get('ajax').request('/' + this.namespace + '/hitcounts/', {
            method: 'POST',
            data: {'topic': this.topic.id}
        }).then(response => {
            this.set('hitTopic', response.data.total);

            //Is completed
            this.set('isLoaded', true);
        });
    },

    /**
    * @method: getCheckUserLike
    * @description: Check if user logged make like in topic
    */
    getCheckUserLike() {
        this.get('ajax').request('/' + this.namespace + '/liketopics/', {
            method: 'GET',
            data: {
                'topic': this.topicId,
                'user': this.userLogin,
                'filter': 'check_like_exists'
            },
            headers: {"Authorization": "jwt " + this.jwt}
        }).then((response) => {
            if(response.data.length > 0) {
                this.set('showLike', false);
            }
        });
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
                    headers: {"Authorization": "jwt " + this.jwt}
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
                headers: {"Authorization": "jwt " + this.jwt}
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
            Ember.$('.tiny.topic_'+id+'.modal').modal({
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

            Ember.$('.tiny.topic_'+id+'.modal').modal('hide');

            this.topic.destroyRecord().then(() => {
                this.sendAction('redirectForum', forum_id, forum_slug);
            });
        },
        /**
        * @method openTopic
        * @description: Open topic in db
        */
        openTopic() {
            this.get('ajax').request('/' + this.namespace + '/open-close-topic/', {
                method: 'POST',
                data: {
                    'user': this.userLogin,
                    'topic': this.topic.id,
                    'is_close': 0
                },
                headers: {"Authorization": "jwt " + this.jwt}
            }).then(() => {
                this.topic.set('isClose', false);
            });
        },
        /**
        * @method closeTopic
        * @description: Close topic in db
        */
        closeTopic() {
            this.get('ajax').request('/' + this.namespace + '/open-close-topic/', {
                method: 'POST',
                data: {
                    'user': this.userLogin,
                    'topic': this.topic.id,
                    'is_close': 1
                },
                headers: {"Authorization": "jwt " + this.jwt}
            }).then(() => {
                this.topic.set('isClose', true);
            });
        },
        /**
        * @method replyComment
        * @description: Go to reply form
        */
        replyComment() {
            if(this.get('session.isAuthenticated')) {
                Ember.$("#reply_comment").focus()
            } else {
                showModalLogin();
            }
        }
    }
});
