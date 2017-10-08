import { inject as service} from '@ember/service';
import { computed } from "@ember/object";
import AjaxService from 'ember-ajax/services/ajax';

export default AjaxService.extend({
    session: service('session'),

    headers: computed('session.data.authenticated.token', {
        get() {
            let headers = {};
            const authToken = this.get('session').session.content.authenticated.token;
            if (authToken) {
                headers['Authorization'] = `jwt ${authToken}`;
            }
            return headers;
        }
    })
});
