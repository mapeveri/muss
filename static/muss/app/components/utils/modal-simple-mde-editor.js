import Component from '@ember/component';
import $ from 'jquery';

export default Component.extend({
    //For check if is the section actions
    sectionActions: {isSectionActions: true},

    actions: {
        /**
        * @method closeModal
        * @description: Close modal and remove padding for fixed scroll
        */
        closeModal() {
            $("#" + this.modalId).hide();
            $("#" + this.contentId).removeClass("paddingEditorMde");
        },
    }
});
