import Ember from 'ember';
import ENV from './../config/environment';

export default Ember.Component.extend({
    ajax: Ember.inject.service(),
    session: Ember.inject.service('session'),
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
        }

        //Check user like in topic
        this.getCheckUserLike();

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
        }
    }
});
