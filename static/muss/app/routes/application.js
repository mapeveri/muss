import Ember from 'ember';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';

export default Ember.Route.extend(ApplicationRouteMixin, {
    session: Ember.inject.service('session'),

    /**
    * @method renderTemplate
    * @description: Render all templates and show loading before
    */
    renderTemplate() {
        this.render('loading');
        this._super();
    },
});
