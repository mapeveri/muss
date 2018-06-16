import Ember from 'ember';
import DS from 'ember-data';
import { inject as service} from '@ember/service';
import { isEmpty } from '@ember/utils';
import ENV from '../config/environment';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
    session: service('session'),

    namespace: ENV.APP.API_NAMESPACE,
    host: ENV.APP.API_HOST,

    buildURL: function(type, id) {
        var url = this._super(type, id);

        if (url.charAt(url.length -1) !== '/') {
          url += '/';
        }

        return url;
    },
    authorize(xhr) {
        if (Ember.testing) {
            xhr.setRequestHeader('Authorization', 'jwt beyonce');
        } else {
            const { token } = this.get('session.data.authenticated');
            if (this.get('session.isAuthenticated') && !isEmpty(token)) {
                xhr.setRequestHeader('Authorization', `jwt ${token}`);
            }
        }
    }
});
