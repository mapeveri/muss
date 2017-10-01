import Ember from 'ember';

export default Ember.Component.extend({
    session: Ember.inject.service('session'),
    currentUser: Ember.inject.service('current-user'),
    isCreatorComment: false,

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            //Check if user logged is the creator of comment
            let user_login = parseInt(this.get('currentUser').user.id);
            let user_comment = this.get('comment.user.id');
            if(user_login == user_comment) {
                this.set('isCreatorComment', true);
            }
        }
    },
    actions: {
        /**
        * @method confirmRemoveComment
        * @description: Display modal for confirm remove comment
        * @param {*} id
        */
        confirmRemoveComment(id) {
            Ember.$('.tiny.'+id+'.modal').modal({
                onApprove: () => {
                  return false;
                }
            }).modal('show');
        },
        /**
        * @method removeComment
        * @description: Remove comment in the db
        */
        removeComment() {
            let id = this.comment.id;
            this.comment.deleteRecord();
            this.comment.save();

            this.get('comments.content').removeObject(this.comment._internalModel);

            Ember.$('.tiny.'+id+'.modal').modal('hide');
        }
    }
});
