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
            $('#content-profile').hide('slow');
            $('#content-profile-edit').removeClass('hide');
            $('#content-profile-edit').show('slow');
        },
        /**
        * @method editProfile
        * @description: Save form profile in db
        */
        editProfile(e) {
            e.preventDefault();

            this.profile.save().then(() => {
                $('#content-profile-edit').hide('slow');
                $('#content-profile-edit').addClass('hide');
                $('#content-profile').show('slow');
            }).catch((err) => {
                this.set('errorMessage', err.errors)
            });
        }
    }
});
