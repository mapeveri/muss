import Service, { inject as service} from "@ember/service";
import RSVP from "rsvp";

export default Service.extend({
    session: service('session'),

    /**
    * @description Get user logged
    */
    init() {
        if (this.get('session.isAuthenticated')) {
            return this.set('user', this.get('session.data.authenticated.user'));
        } else {
            return RSVP.resolve();
        }
    }
});
