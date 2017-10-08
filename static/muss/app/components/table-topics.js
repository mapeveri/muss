import Component from '@ember/component';

export default Component.extend({
    actions: {
        /**
        * @method goTop
        * @description: Go top scroll browser
        */
        goTop() {
            window.scrollTo(0, 0);
        }
    }
});
