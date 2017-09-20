import Ember from 'ember';
import { gettextHelper } from '../../helpers/gettext';

export default Ember.Component.extend({
    id: 'login-form',
    errorMessage: [],
    session: Ember.inject.service('session'),
    actions: {
        /**
        * @method: init
        * @description: Initialize form
        */
        init() {
            this.set('errorMessage', []);
            this.set('user', '');
            this.set('password', '');
        },
        /**
        * @method: authenticate
        * @description: Login authentication
        */
        authenticate() {
            let self = this;
            let { user, password } = this.getProperties('user', 'password');

            if(Ember.isEmpty(user) || Ember.isEmpty(password)) {
                this.set('errorMessage', {'errors': {'non_field_errors': [gettextHelper("Username or password incorrect.")]}});
            } else {
                this.get('session').authenticate('authenticator:jwt', user, password).then(() => {
                    Ember.$('.tiny.'+self.id+'.modal').modal("hide");
                }).catch((reason) => {
                    this.set('errorMessage', reason.responseJSON);
                });
            }
        }
    }
});
