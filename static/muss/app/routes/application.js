import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';

export default Route.extend(ApplicationRouteMixin, {
    session: service('session'),
    currentUser: service('current-user'),

    model() {
        if(this.get('currentUser').user != undefined) {
            return this.get('store').query('notification', {"user": parseInt(this.get('currentUser').user.id), "limit": 10});
        } else {
            return [];
        }
    },
    /**
    * @method renderTemplate
    * @description: Render all templates and show loading before
    */
    renderTemplate() {
        this.render('loading');
        this._super();
    },
});
