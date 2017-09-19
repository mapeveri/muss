import Ember from 'ember';

export default Ember.Component.extend({
    id: 'login-form',
    session: Ember.inject.service('session'),

    actions: {
        /**
        * @method: authenticate
        * @description: Login authentication
        */
        authenticate() {
            let self = this;
            let { user, password } = this.getProperties('user', 'password');
            this.get('session').authenticate('authenticator:jwt', user, password).then(() => {
                Ember.$('.tiny.'+self.id+'.modal').modal("hide");
            }).catch((reason) => {
                this.set('errorMessage', reason.responseJSON);
            });
        }
    }
});
