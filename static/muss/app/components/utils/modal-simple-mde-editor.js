import Component from '@ember/component';
import $ from 'jquery';

export default Component.extend({
    //For check if is the section actions
    sectionActions: {isSectionActions: true},
    sectionContent: {isSectionContent: true},
    contentClass: 'paddingEditorMde',

    didInsertElement() {
        let contentId = this.get('contentId');
        $("#" + this.modalId).on('open', () => {
            //Add content fixed scroll
            $("#" + contentId).addClass(this.contentClass);
        });

        $("#" + this.modalId).on('close', () => {
            //Remove content fixed scroll
            $("#" + contentId).removeClass(this.contentClass);
        });
    },
    actions: {
        /**
        * @method closeModal
        * @description: Close modal and remove padding for fixed scroll
        */
        closeModal() {
            //Hide modal editor
            $("#" + this.modalId).removeClass('mde-modal-content-open').height(0).trigger("close");
        },
    }
});
