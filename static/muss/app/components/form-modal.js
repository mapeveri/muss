import Ember from 'ember';

export default Ember.Component.extend({
    title: '',
    title_action: '',
    id: '',

    actions: {
        /**
        * @method: showForm
        * @description: Display modal form
        */
        showForm() {
            Ember.$('.tiny.'+this.id+'.modal').modal({
                onApprove: () => {
                  return false;
                }
              }).modal('show');
        },
        /**
        * @method: action
        * @description: Call action param
        */
        action() {
            this.attrs['action'](...arguments);
        }
    }
});
