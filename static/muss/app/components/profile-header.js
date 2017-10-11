import Component from '@ember/component';
import { inject as service} from '@ember/service';

export default Component.extend({
    canEdit: false,
    session: service('session'),
    currentUser: service('current-user'),

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            let user_login = parseInt(this.get('currentUser').user.id);
            let is_troll = this.get('profile.isTroll');
            let profile_user_id = parseInt(this.get('profile.user.id'));

            //Check if can edit profile
            if(user_login == profile_user_id && !is_troll) {
                this.set('canEdit', true);
            }
        }
    }
});
