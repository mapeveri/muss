import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { gettextHelper } from '../../helpers/gettext';

export default Component.extend({
    id: 'login-form',
    session: service('session'),

    actions: {
        /**
        * @method init
        * @description: Initialize form
        */
        init() {
            this.actions.resetErrors(this);
            this.set('user', '');
            this.set('password', '');
        },
        /**
        * @method resetErrors
        * @description: Reset errors messages
        */
        resetErrors(self) {
            self.set('errorMessage', '');
        },
        /**
        * @method authenticate
        * @description: Login authentication
        */
        authenticate() {
            this.actions.resetErrors(this);
            let { user, password } = this.getProperties('user', 'password');

            if(!isPresent(user) || !isPresent(password)) {
                this.set('errorMessage', gettextHelper("Username or password incorrect."));
            } else {
                this.get('session').authenticate('authenticator:jwt', user, password).then(() => {
                    $('.tiny.'+this.id+'.modal').modal("hide");
                }).catch((reason) => {
                    this.set('errorMessage', reason.responseJSON.errors.non_field_errors);
                });
            }
        }
    }
});
