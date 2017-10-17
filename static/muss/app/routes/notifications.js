import Route from '@ember/routing/route';
import { inject as service} from '@ember/service';

export default Route.extend({
    session: service('session'),
    currentUser: service('current-user'),

    beforeModel() {
        if(!this.get('session').session.isAuthenticated) {
            this.transitionTo('index');
            return false;
        }
    },
    model() {
        let user_id = parseInt(this.get('currentUser').user.id);
        return this.get('store').query('notification', {"user": user_id});
    }
});
