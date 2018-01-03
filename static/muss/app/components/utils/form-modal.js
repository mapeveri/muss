import Component from '@ember/component';
import { get } from "@ember/object"
import $ from 'jquery';

export default Component.extend({
    //Title modal
    title_modal: '',
    //Title action unique
    title_action: '',
    //Id modal
    id: '',
    //If show button or link for display modal
    hasUiForShowModal: true,
    //Check if has custom actions or manage a unique action (this is default)
    customActions: false,
    //For check if is the section default content
    sectionContent: {isSectionContent: true},
    //For check if is the section actions
    sectionActions: {isSectionActions: true},

    actions: {
        /**
        * @method showForm
        * @description: Display modal form
        */
        showForm() {
            $('.tiny.'+this.id+'.modal').modal({
                onApprove: () => {
                  return false;
                }
            }).modal('show');
            //Reset form
            get(this, 'initialize')(...arguments);
        },
        /**
        * @method cancelModal
        * @description: Cancel modal
        */
        cancelModal() {
            $('.tiny.'+this.id+'.modal').modal('hide');
        },
        /**
        * @method action
        * @description: Call action param
        */
        action() {
            get(this, 'action')(...arguments);
        }
    }
});
