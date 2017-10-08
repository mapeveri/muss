import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { gettextHelper } from '../../helpers/gettext';

export default Component.extend({
    ajax: service('ajax'),
    uidb64: null,
    token: null,
    csrftoken: null,
    self: this,
    isValidLink: false,
    isSuccess: false,

    didInsertElement() {
        this._super();
        this.csrftoken = $("[name=csrfmiddlewaretoken]").first().val();
        this.actions.resetErrors(this);

        //Check if is valid link email
        this.get('ajax').request('/reset/', {
            method: 'POST',
            dataType: 'html',
            data: {
                valid_link: 1,
                uidb64: this.uidb64,
                token: this.token,
                csrfmiddlewaretoken: this.csrftoken,
            }
        }).then(() => {
            this.set('isValidLink', true);
        }).catch(() => {
            window.location = "/";
        })
    },
    actions: {
        /**
        * @method resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorMessage', '');
            self.set('errorPassword1', '');
            self.set('errorPassword2', '');
        },
        /**
        * @method setNewPassowrd
        * @description: Update password
        */
        setNewPassowrd() {
            this.actions.resetErrors(this);
            let { new_password1, new_password2 } = this.getProperties('new_password1', 'new_password2');
            let isValid = true;

            if(!isPresent(new_password1)) {
                this.set('errorPassword1', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!isPresent(new_password2)) {
                this.set('errorPassword2', gettextHelper("This field is required."));
                isValid = false;
            }

            if(new_password1 != new_password2) {
                this.set('errorPassword2', gettextHelper("Passwords don't match"));
                isValid = false;
            }

            if(isValid) {
                this.get('ajax').request('/reset/', {
                    method: 'POST',
                    dataType: 'html',
                    data: {
                        valid_link: 0,
                        uidb64: this.uidb64,
                        token: this.token,
                        password: new_password1,
                        csrfmiddlewaretoken: this.csrftoken,
                    }
                }).then((response) => {
                    let res = JSON.parse(response);
                    if (res.status == 200) {
                        if(res.message) {
                            this.set('errorMessage', res.message);
                        } else {
                            this.set('isValidLink', false);
                            this.set('isSuccess', true);
                        }
                    }
                }).catch(() => {
                    window.location = "/";
                });
            }
        }
    }
});
