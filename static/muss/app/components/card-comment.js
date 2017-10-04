import Ember from 'ember';
import ENV from './../config/environment';

export default Ember.Component.extend({
    ajax: Ember.inject.service('ajax'),
    session: Ember.inject.service('session'),
    currentUser: Ember.inject.service('current-user'),
    namespace: ENV.APP.API_NAMESPACE,
    isCreatorComment: false,
    userLogin: null,
    commentId: null,
    showLike: true,
    jwt: null,

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            //Check if user logged is the creator of comment
            let user_login = parseInt(this.get('currentUser').user.id);
            this.set('userLogin', user_login);
            let user_comment = this.get('comment.user.id');
            if(user_login == user_comment) {
                this.set('isCreatorComment', true);
            }

            this.set('commentId', this.get('comment.id'));
            this.set('jwt', this.get('session').session.content.authenticated.token);

            this.get('ajax').request('/' + this.namespace + '/likecomments/', {
                method: 'GET',
                data: {
                    'comment': this.commentId,
                    'user': this.userLogin,
                    'filter': 'check_like_exists'
                },
                headers: {"Authorization": "jwt " + this.jwt}
            }).then((response) => {
                if(response.data.length > 0) {
                    this.set('showLike', false);
                }
            });
        }
    },
    actions: {
        /**
        * @method confirmRemoveComment
        * @description: Display modal for confirm remove comment
        * @param {*} id
        */
        confirmRemoveComment(id) {
            Ember.$('.tiny.comment_'+id+'.modal').modal({
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
            Ember.$('.tiny.comment_'+id+'.modal').modal('hide');
        },
        /**
        * @method likeComment
        * @description: Save like comment in db
        */
        likeComment() {
            this.get('ajax').request('/' + this.namespace + '/likecomments/', {
                method: 'POST',
                data: {
                    'comment': this.commentId,
                    'users': this.userLogin
                },
                headers: {"Authorization": "jwt " + this.jwt}
            }).then(() => {
                this.set('showLike', false);
                this.set('comment.totalLikes', this.get('comment.totalLikes') + 1);
            });
        },
        /**
        * @method unLikeComment
        * @description: Delete like comment in db
        */
        unLikeComment() {
            this.get('ajax').request('/' + this.namespace + '/likecomments/' + this.commentId + '/', {
                method: 'DELETE',
                data: {
                    'users': this.userLogin
                },
                headers: {"Authorization": "jwt " + this.jwt}
            }).then(() => {
                this.set('showLike', true);
                this.set('comment.totalLikes', this.get('comment.totalLikes') - 1);
            });
        }
    }
});
