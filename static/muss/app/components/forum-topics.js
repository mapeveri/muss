import Ember from 'ember';
import config from './../config/environment';

export default Ember.Component.extend({
    session: Ember.inject.service('session'),
    currentUrl: window.location.href,
    rssUrl: config.APP.API_HOST + "/" + "feed/"
});
