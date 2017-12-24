import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import UnAuthenticatedRouteMixin from 'ember-simple-auth/mixins/unauthenticated-route-mixin';
import $ from 'jquery';

export default Route.extend(UnAuthenticatedRouteMixin, {
    ajax: service('ajax'),

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
