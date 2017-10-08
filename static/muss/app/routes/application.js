import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import ApplicationRouteMixin from 'ember-simple-auth/mixins/application-route-mixin';

export default Route.extend(ApplicationRouteMixin, {
    session: service('session'),

    /**
    * @method renderTemplate
    * @description: Render all templates and show loading before
    */
    renderTemplate() {
        this.render('loading');
        this._super();
    },
});
