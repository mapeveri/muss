import Ember from 'ember';

export default Ember.Controller.extend({
    session: Ember.inject.service('session'),

    actions: {
        /**
        * @method: invalidateSession
        * @description: Logout
        */
        invalidateSession() {
            this.get('session').invalidate();
        },
        /**
        * @method onSearch
        * @description: Event onkeyup input search
        * @param {*} q
        */
        onSearch(q) {
            this.transitionToRoute('search-topic', { queryParams: { q: q } });
        }
    }
});
