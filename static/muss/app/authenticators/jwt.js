import Ember from 'ember';
import Base from 'ember-simple-auth/authenticators/base';
import ENV from '../config/environment';

const { RSVP: { Promise } } = Ember;

export default Base.extend({
    tokenEndpoint: ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE + '/token-auth/',
    verifyTokenEndpoint: ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE + '/api-token-verify/',
    restore(data) {
        return new Promise((resolve, reject) => {
            if (!Ember.isEmpty(data.token)) {
                const requestOptions = {
                    url: this.verifyTokenEndpoint,
                    type: 'POST',
                    contentType: "application/x-www-form-urlencoded",
                    data: {
                        token: data.token,
                    },
                };
                let promise = new Promise((resolve, reject) => {
                    Ember.$.ajax(requestOptions).then(() => {
                        resolve();
                    }, () => {
                        reject();
                    });
                });

                return promise.then(() => {
                    resolve(data);
                }).catch(() => {
                    reject();
                })
            } else {
                reject();
            }
        });
    },
    authenticate(identification, password) {
        const requestOptions = {
            url: this.tokenEndpoint,
            type: 'POST',
            contentType: "application/x-www-form-urlencoded",
            data: {
                username: identification,
                password: password,
            },
        };
        return new Promise((resolve, reject) => {
            Ember.$.ajax(requestOptions).then((response) => {
                let jwt = response.data.token;
                let user = response.data.user;
                Ember.run(() => {
                    resolve({
                        token: jwt,
                        user: user,
                    });
                });
            }, (error) => {
                Ember.run(() => {
                    reject(error);
                });
            });
        });
    },
    invalidate(data) {
        return Promise.resolve(data);
    }
});
