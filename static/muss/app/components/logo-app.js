import Ember from 'ember';

export default Ember.Component.extend({
    logo: (typeof(window.muss) === "undefined" ? "" : window.muss.logo),
    width: (typeof(window.muss) === "undefined" ? "" : window.muss.logo_width + "px"),
    height: (typeof(window.muss) === "undefined" ? "" : window.muss.logo_height + "px"),
    styles: '',

    didInsertElement() {
        this._super();
        this.getStyles();
    },

    /**
    * @method: getStyles
    * @description: Get styles for logo app
    */
    getStyles() {
        let styles = "";
        let width = this.get('width');
        let height = this.get('height');

        // With width and height
        if(width != "" && height != "") {
            styles += "width: " + width + "; height: " + height;
        // If only widht
        } else if(width != "" && height == "") {
            styles += "width: " + width + ";";
        // If only height
        } else if(width == "" && height != "") {
            styles += "height: " + height + ";";
        }

        this.set('styles', styles);
    },
});
