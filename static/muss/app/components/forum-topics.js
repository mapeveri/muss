import Ember from 'ember';
import config from './../config/environment';

export default Ember.Component.extend({
    currentUrl: window.location.href,
    rssUrl: config.APP.API_HOST + "/" + "feed/"
});
