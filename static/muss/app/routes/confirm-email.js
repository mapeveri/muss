import Ember from 'ember';

export default Ember.Route.extend({
    ajax: Ember.inject.service(),
    session: Ember.inject.service('session'),
    beforeModel() {
        if(this.get('session').session.isAuthenticated) {
            this.transitionTo('index');
            return false;
        }
    },
    model(params) {
        let csrftoken = Ember.$("[name=csrfmiddlewaretoken]").first().val();
        return this.get('ajax').request('/confirm-email/', {
            method: 'POST',
            dataType: 'html',
            data: {
                username: params.username,
                activation_key: params.activation_key,
                csrfmiddlewaretoken: csrftoken,
            }
        }).then(response => {
            return response;
        });
    },
});
