import Component from '@ember/component';
import { inject as service} from '@ember/service';

export default Component.extend({
    session: service('session'),
    isTrollUser: false,

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            //Check if is a troll user
            this.set('isTrollUser', this.get('profile.isTroll'));
        }
    }
});
