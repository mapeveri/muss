import Ember from 'ember';
import { gettextHelper } from '../../helpers/gettext';

export default Ember.Component.extend({
    ajax: Ember.inject.service(),
    uidb64: null,
    token: null,
    errorMessage: null,
    errorPassword1: null,
    errorPassword2: null,
    csrftoken: Ember.$("[name=csrfmiddlewaretoken]").first().val(),
    self: this,
    isValidLink: false,
    isSuccess: false,

    didInsertElement() {
        this._super();
        let self = this;

        this.actions.resetErrors(this);

        //Check if is valid link email
        this.get('ajax').request('/reset/', {
            method: 'POST',
            dataType: 'html',
            data: {
                valid_link: 1,
                uidb64: self.uidb64,
                token: self.token,
                csrfmiddlewaretoken: self.csrftoken,
            }
        }).then(() => {
            this.set('isValidLink', true);
        }).catch(() => {
            window.location = "/";
        })
    },
    actions: {
        /**
        * @method: resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorMessage', '');
            self.set('errorPassword1', '');
            self.set('errorPassword2', '');
        },
        /**
        * @method: setNewPassowrd
        * @description: Update password
        */
        setNewPassowrd() {
            this.actions.resetErrors(this);

            let { new_password1, new_password2 } = this.getProperties('new_password1', 'new_password2');
            let self = this;
            let isValid = true;

            if(!Ember.isPresent(new_password1)) {
                this.set('errorPassword1', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!Ember.isPresent(new_password2)) {
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
                        uidb64: self.uidb64,
                        token: self.token,
                        password: new_password1,
                        csrfmiddlewaretoken: self.csrftoken,
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
