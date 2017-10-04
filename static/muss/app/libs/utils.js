import Ember from 'ember';

/**
* @method validateEmail
* @description: Check if is valid email
* @param {*} email
*/
export function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

/**
* @method showModalLogin
* @description: Display the modal form login
*/
export function showModalLogin() {
    Ember.$('.tiny.login-form.modal').modal("show");
}
