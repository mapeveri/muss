import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import $ from 'jquery';

export default Route.extend({
    ajax: service('ajax'),
    session: service('session'),
    beforeModel() {
        if(this.get('session').session.isAuthenticated) {
            this.transitionTo('index');
            return false;
        }
    },
    model(params) {
        let csrftoken = $("[name=csrfmiddlewaretoken]").first().val();
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
        }).catch(() => {
            this.transitionTo('index');
        });
    },
});
