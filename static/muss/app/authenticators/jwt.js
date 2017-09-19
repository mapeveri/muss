import Ember from 'ember';
import Base from 'ember-simple-auth/authenticators/base';

const { RSVP: { Promise } } = Ember;

export default Base.extend({
    tokenEndpoint: '/api/token-auth/',
    restore(data) {
        return new Promise((resolve, reject) => {
            if (!Ember.isEmpty(data.token)) {
                resolve(data);
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
