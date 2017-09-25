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
            this.actions.resetErrors(this);
            this.set('email', '');
        },
        /**
        * @method: resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorEmail', '');
        },
        /**
        * @method: reset
        * @description: Reset password
        */
        reset() {
            this.actions.resetErrors(this);

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

                let csrftoken = Ember.$("[name=csrfmiddlewaretoken]").first().val();
                return this.get('ajax').request('/reset-password/', {
                    method: 'POST',
                    data: {
                        email: email,
                        csrfmiddlewaretoken: csrftoken,
                    }
                }).then(() => {
                    Ember.$('.tiny.'+self.id+'.modal').modal("hide");
                    window.toastr.success(gettextHelper('Please, check your email.'));
                }).catch(() => {
                    this.set('errorEmail', gettextHelper("Error sending email."));
                });
            }
        }
    }
});
