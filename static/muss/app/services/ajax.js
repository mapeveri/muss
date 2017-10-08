import Ember from 'ember';
import AjaxService from 'ember-ajax/services/ajax';

export default AjaxService.extend({
    session: Ember.inject.service(),

    headers: Ember.computed('session.data.authenticated.token', {
        get() {
            let headers = {};
            const authToken = this.get('session').session.content.authenticated.token;
            if (authToken) {
                headers['Authorization'] = `jwt ${authToken}`;
            }
            return headers;
        }
    })
});
