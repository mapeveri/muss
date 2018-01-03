import { run } from '@ember/runloop';
import { isEmpty } from '@ember/utils';
import { Promise } from 'rsvp';
import Base from 'ember-simple-auth/authenticators/base';
import $ from 'jquery';
import ENV from '../config/environment';

export default Base.extend({
    tokenEndpoint: ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE + '/token-auth/',
    verifyTokenEndpoint: ENV.APP.API_HOST + '/' + ENV.APP.API_NAMESPACE + '/api-token-verify/',
    restore(data) {
        return new Promise((resolve, reject) => {
            if (!isEmpty(data.token)) {
                const requestOptions = {
                    url: this.verifyTokenEndpoint,
                    type: 'POST',
                    contentType: "application/x-www-form-urlencoded",
                    data: {
                        token: data.token,
                    },
                };
                let promise = new Promise((resolve, reject) => {
                    $.ajax(requestOptions).then(() => {
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
            $.ajax(requestOptions).then((response) => {
                let jwt = response.data.token;
                let user = response.data.user;
                run(() => {
                    resolve({
                        token: jwt,
                        user: user,
                    });
                });
            }, (error) => {
                run(() => {
                    reject(error);
                });
            });
        });
    },
    invalidate(data) {
        return Promise.resolve(data);
    }
});
