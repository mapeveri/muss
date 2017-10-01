import Ember from 'ember';
import ENV from './../config/environment';

export default Ember.Component.extend({
    ajax: Ember.inject.service(),
    session: Ember.inject.service('session'),
    currentUser: Ember.inject.service('current-user'),
    currentUrl: window.location.href,
    isLoaded: false,
    topic: null,
    hitTopic: null,
    isCreatorTopic: false,
    isLikeTopicUser: false,
    totalCommentsWatcher: function() {
        this.set('topic.totalComments', this.get('comments.content').length);
    }.observes('comments.content.[]'),

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            //Check if user logged is the creator of topic
            let user_login = parseInt(this.get('currentUser').user.id);
            let user_topic = this.get('topic.user.id');
            if(user_login == user_topic) {
                this.set('isCreatorTopic', true);
            }

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
        let namespace = ENV.APP.API_NAMESPACE;
        return this.get('ajax').request('/' + namespace + '/hitcounts/', {
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
        let namespace = ENV.APP.API_NAMESPACE;
        return this.get('ajax').request('/' + namespace + '/check-user-like-topic/', {
            method: 'POST',
            data: {'topic_id': this.topic.id, 'user_id': this.get('topic.user.id')}
        }).then(response => {
            this.set('isLikeTopicUser', response.data.is_like);
        });
    }
});
