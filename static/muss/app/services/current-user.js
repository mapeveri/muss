import Ember from 'ember';

const { inject: { service }, RSVP } = Ember;

export default Ember.Service.extend({
    session: service('session'),

    /**
    * @description: Get user logged
    */
    init() {
        if (this.get('session.isAuthenticated')) {
            return this.set('user', this.get('session.data.authenticated.user'));
        } else {
            return RSVP.resolve();
        }
    }
});
