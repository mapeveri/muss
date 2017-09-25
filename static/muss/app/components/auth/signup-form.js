import Ember from 'ember';
import { gettextHelper } from '../../helpers/gettext';
import { validateEmail } from '../../libs/utils';

export default Ember.Component.extend({
    id: 'signup-form',
    store: Ember.inject.service('store'),

    actions: {
        /**
        * @method: init
        * @description: Initialize form
        */
        init() {
            this.actions.resetErrors(this);

            this.set('firstname', '');
            this.set('lastname', '');
            this.set('email', '');
            this.set('username', '');
            this.set('password', '');
            this.set('repeat_password', '');
        },
        /**
        * @method: resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorMessage', [])
            self.set('errorFirstname', '');
            self.set('errorLastname', '');
            self.set('errorEmail', '');
            self.set('errorUsername', '');
            self.set('errorPassword', '');
            self.set('errorRepeatPassword', '');
            self.set('errorCheckPassword', '');
        },
        /**
        * @method: signup
        * @description: Create user
        */
        signup() {
            this.actions.resetErrors(this);

            let firstname = this.get('firstname');
            let lastname = this.get('lastname');
            let email = this.get('email');
            let username = this.get('username');
            let password = this.get('password');
            let repeat_password = this.get('repeat_password');
            let isValid = true;

            if(!Ember.isPresent(firstname)) {
                this.set('errorFirstname', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!Ember.isPresent(lastname)) {
                this.set('errorLastname', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!Ember.isPresent(email)) {
                this.set('errorEmail', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!validateEmail(email)) {
                this.set('errorEmail', gettextHelper("Email is invalid."));
                return false;
            }

            if(!Ember.isPresent(username)) {
                this.set('errorUsername', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!Ember.isPresent(password)) {
                this.set('errorPassword', gettextHelper("This field is required."));
                isValid = false;
            }

            if(!Ember.isPresent(repeat_password)) {
                this.set('errorRepeatPassword', gettextHelper("This field is required."));
                isValid = false;
            }

            if(password != repeat_password) {
                this.set('errorCheckPassword', gettextHelper("Passwords don't match"));
                isValid = false;
            }

            if(isValid) {
                let user = this.get('store').createRecord('user', {
                    'firstName': firstname,
                    'lastName': lastname,
                    'username': username,
                    'email': email,
                    'password': password
                });

                let self = this;
                user.save().then(() => {
                    Ember.$('.tiny.'+self.id+'.modal').modal("hide");
                    window.toastr.success(gettextHelper('Please, check your email.'));
                }).catch((err) => {
                    this.set('errorMessage', err.errors)
                });
            }
        }
    }
});
