import Ember from 'ember';
import ENV from './../config/environment';

export default Ember.Component.extend({
    ajax: Ember.inject.service(),
    session: Ember.inject.service('session'),
    currentUrl: window.location.href,
    isLoaded: false,
    topic: null,
    hitTopic: null,

    didInsertElement() {
        this._super();
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
    }
});
