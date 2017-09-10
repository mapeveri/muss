import Ember from 'ember';
import ENV from '../config/environment';

export function getUrlApi() {
    return ENV.APP.API_HOST + "/" + ENV.APP.API_NAMESPACE + "/";
}

export function ajax(url) {
    const options = {
        url: url,
        type: 'GET',
        dataType: 'jsonp',
        accept: 'application/vnd.api+json',
        headers: {
          "Content-Type": 'application/vnd.api+json'
        }
    };
  
    return Ember.$.ajax(options);
}