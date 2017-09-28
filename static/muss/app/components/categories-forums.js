import Ember from 'ember';

export default Ember.Component.extend({
    didRender() {
        this._super();
        //Hide loading
        this.get('loadingSpinner').set('loading', false);
    }
});
