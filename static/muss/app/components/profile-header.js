import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';
import { getValidTypesImage } from '../libs/utils';
import { gettextHelper } from '../helpers/gettext';

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
        * @method setPhoto
        * @description: Set photo profile dynamic
        */
        setPhoto() {
            const file = $('#photo_id')[0].files[0];
            const validImageTypes = getValidTypesImage();

            if ($.inArray(file['type'], validImageTypes) > 0) {
                const reader = new FileReader();

                this.profile.set('photo', file);
                let imageData;

                //Reading file is async
                reader.onload = () => {
                    imageData = reader.result;
                    this.set('profile.user.userPhoto', imageData);
                };

                if (file) {
                    reader.readAsDataURL(file);
                }
            } else {
                this.set('errorMessage', [{'detail': gettextHelper('Incorrect image type')}])
            }
        },
        /**
        * @method editProfile
        * @description: Save form profile in db
        */
        editProfile() {
            let clear = $("#clear_photo").is(":checked");
            if(clear) {
                this.profile.set('photo', null);
            }

            this.profile.save().then(() => {
                if(clear) {
                    window.location.reload();
                } else {
                    $('#content-profile-edit').hide('slow');
                    $('#content-profile-edit').addClass('hide');
                    $('#content-profile').show('slow');
                }
            }).catch((err) => {
                this.set('errorMessage', err.errors)
            });
        }
    }
});
