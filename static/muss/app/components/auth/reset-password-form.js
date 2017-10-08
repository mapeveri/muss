import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { gettextHelper } from '../../helpers/gettext';
import { validateEmail } from '../../libs/utils';

export default Component.extend({
    id: 'reset-password-form',
    ajax: service('ajax'),

    actions: {
        /**
        * @method init
        * @description: Initialize form
        */
        init() {
            this.actions.resetErrors(this);
            this.set('email', '');
        },
        /**
        * @method resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorEmail', '');
        },
        /**
        * @method reset
        * @description: Reset password
        */
        reset() {
            this.actions.resetErrors(this);
            let { email } = this.getProperties('email');

            if(!validateEmail(email)) {
                this.set('errorEmail', gettextHelper("Email is invalid."));
                return false;
            }

            if(!isPresent(email)) {
                this.set('errorEmail', gettextHelper("This field is required."));
            } else {
                this.set('errorEmail', '');

                let csrftoken = $("[name=csrfmiddlewaretoken]").first().val();
                return this.get('ajax').request('/reset-password/', {
                    method: 'POST',
                    data: {
                        email: email,
                        csrfmiddlewaretoken: csrftoken,
                    }
                }).then(() => {
                    $('.tiny.'+this.id+'.modal').modal("hide");
                    window.toastr.success(gettextHelper('Please, check your email.'));
                }).catch(() => {
                    this.set('errorEmail', gettextHelper("Error sending email."));
                });
            }
        }
    }
});
