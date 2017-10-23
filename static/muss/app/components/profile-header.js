import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';
import { getValidTypesImage, setTitlePage } from '../libs/utils';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    session: service('session'),
    store: service('store'),
    currentUser: service('current-user'),
    idFormEdit: 'form-edit-profile',
    canEdit: false,
    setTitleHtml: function() {
        this.updateTitleHtml();
    }.observes('profile.user.username'),

    didInsertElement() {
        this._super();

        //Change title html
        this.updateTitleHtml();

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
    /**
    * @method updateTitleHtml
    * @description: Change title html
    */
    updateTitleHtml() {
        setTitlePage(gettextHelper("Profile") + " - " + this.get('profile.user.username'));
    },
    actions: {
        /**
        * @method showModalEditProfile
        * @description: Display form edit profile
        */
        showModalEditProfile() {
            $('#content-profile').hide('slow');
            $('#content-profile-edit').removeClass('hide');
            $('#content-profile-edit').show('slow');
        },
        /**
        * @method hideEditProfile
        * @description: Hide edit form
        */
        hideEditProfile() {
            $('#content-profile-edit').hide('slow');
            $('#content-profile-edit').addClass('hide');
            $('#content-profile').show('slow');
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

            let self = this;
            this.profile.save().then(() => {
                if(clear) {
                    window.location.reload();
                } else {
                    self.actions.hideEditProfile();
                }
            }).catch((err) => {
                this.set('errorMessage', err.errors)
            });
        },
    }
});
