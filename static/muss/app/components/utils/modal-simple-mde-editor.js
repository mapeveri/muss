import Ember from 'ember';

export default Ember.Component.extend({
    //For check if is the section actions
    sectionActions: {isSectionActions: true},

    actions: {
        /**
        * @method closeModal
        * @description: Close modal and remove padding for fixed scroll
        */
        closeModal() {
            Ember.$("#" + this.modalId).hide();
            Ember.$("#" + this.contentId).removeClass("paddingEditorMde");
        },
    }
});
