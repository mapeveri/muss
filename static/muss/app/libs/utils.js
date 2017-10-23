import $ from 'jquery';

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
    $('.tiny.login-form.modal').modal("show");
}

/**
* @method closeAllEditor
* @description: Close all editor mde
*/
export function closeAllEditor() {
    $(".mde-modal-content").removeClass('mde-modal-content-open').height(0).trigger("close");
}

/**
* @method getValidTypesImage
* @description: Get types files valid
*/
export function getValidTypesImage() {
    return ["image/gif", "image/jpeg", "image/png", "image/gif", "image/jpg"];
}

/**
* @method getUrlConnectionWs
* @description: Get url for connect to ws
*/
export function getUrlConnectionWs() {
    let protocol;
    if (window.location.protocol === "https:") {
        protocol = "wss:";
    } else {
        protocol = "ws:";
    }

    let url = protocol + "//" + window.location.hostname + ":8000/ws/";
    return url;
}

/**
* @method setTitlePage
* @description: Update title page
* @param {*} title
*/
export function setTitlePage(title) {
    $(document).attr("title", title);
}
