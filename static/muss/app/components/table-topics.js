import Ember from 'ember';

export default Ember.Component.extend({
    actions: {
        /**
        * @method: goTop
        * @description: Go top scroll browser
        */
        goTop() {
            window.scrollTo(0, 0);
        }
    }
});
