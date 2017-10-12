import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';

export default Component.extend({
    session: service('session'),
    store: service('store'),
    currentUser: service('current-user'),
    idFormEdit: 'form-edit-profile',
    canEdit: false,

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
    },
    actions: {
        /**
        * @method showModalEditProfile
        * @description: Display form modal edit profile
        */
        showModalEditProfile() {
            $('.tiny.'+this.idFormEdit+'.modal').modal({
                onApprove: () => {
                  return false;
                }
            }).modal('show');
        },
        /**
        * @method editProfile
        * @description: Save form profile in db
        */
        editProfile() {
            this.profile.save().then(() => {
                $('.tiny.'+this.idFormEdit+'.modal').modal("hide");
            }).catch((err) => {
                this.set('errorMessage', err.errors)
            });
        }
    }
});
