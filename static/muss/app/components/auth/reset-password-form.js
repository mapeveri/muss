import Ember from 'ember';
import { gettextHelper } from '../../helpers/gettext';
import { validateEmail } from '../../libs/utils';

export default Ember.Component.extend({
    id: 'reset-password-form',
    ajax: Ember.inject.service(),

    actions: {
        /**
        * @method: init
        * @description: Initialize form
        */
        init() {
            this.set('errorEmail', '');
            this.set('email', '');
        },
        /**
        * @method: reset
        * @description: Reset password
        */
        reset() {
            let self = this;
            let { email } = this.getProperties('email');

            if(!validateEmail(email)) {
                this.set('errorEmail', gettextHelper("Email is invalid."));
                return false;
            }

            if(!Ember.isPresent(email)) {
                this.set('errorEmail', gettextHelper("This field is required."));
            } else {
                this.set('errorEmail', '');

                /*return this.get('ajax').request('/reset-password/', {
                    method: 'POST',
                    data: {'email': email}
                }).then(response => {
                    Ember.$('.tiny.'+self.id+'.modal').modal("hide");
                }); */
            }
        }
    }
});
