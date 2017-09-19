import DS from 'ember-data';
import ENV from '../config/environment';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
    namespace: ENV.APP.API_NAMESPACE,
    host: ENV.APP.API_HOST,
    buildURL: function(type, id) {
        var url = this._super(type, id);

        if (url.charAt(url.length -1) !== '/') {
          url += '/';
        }

        return url;
    },
    authorizer: 'authorizer:jwt',
});
