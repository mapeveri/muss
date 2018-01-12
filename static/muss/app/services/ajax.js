import { inject as service} from '@ember/service';
import { computed } from "@ember/object";
import AjaxService from 'ember-ajax/services/ajax';
import config from '../config/environment';

export default AjaxService.extend({
    session: service('session'),
    host: config.APP.API_HOST + "/" + config.APP.API_NAMESPACE,

    headers: computed('session.content.authenticated.token', {
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
