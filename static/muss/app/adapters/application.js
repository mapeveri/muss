import DS from 'ember-data';
import ENV from '../config/environment';

export default DS.JSONAPIAdapter.extend({
    namespace: ENV.APP.API_NAMESPACE,
    host: ENV.APP.API_HOST,
    buildURL: function(type, id) {
        var url = this._super(type, id);
    
        if (url.charAt(url.length -1) !== '/') {
          url += '/';
        }
    
        return url;
    },
});
