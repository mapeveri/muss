import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';
import ENV from './../config/environment';
import { showModalLogin } from '../libs/utils';

export default Component.extend({
    ajax: service('ajax'),
    session: service('session'),
    currentUser: service('current-user'),
    namespace: ENV.APP.API_NAMESPACE,
    isCreatorComment: false,
    userLogin: null,
    commentId: null,
    showLike: true,

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

            //Check if exists like user logged
            let likes = this.get('comment.likes');
            if (likes.length > 0) {
                let exists = likes.find(o => o.user === user_login);
                if(exists != undefined) {
                    this.set('showLike', false);
                }
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
            $('.tiny.comment_'+id+'.modal').modal({
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
            $('.tiny.comment_'+id+'.modal').modal('hide');
        },
        /**
        * @method likeComment
        * @description: Save like comment in db
        */
        likeComment() {
            if(this.get('session.isAuthenticated')) {
                this.get('ajax').request('/' + this.namespace + '/likecomments/', {
                    method: 'POST',
                    data: {
                        'comment': this.commentId,
                        'users': this.userLogin
                    },
                }).then(() => {
                    this.set('showLike', false);
                    this.set('comment.totalLikes', this.get('comment.totalLikes') + 1);
                });
            } else {
                showModalLogin();
            }
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
            }).then(() => {
                this.set('showLike', true);
                this.set('comment.totalLikes', this.get('comment.totalLikes') - 1);
            });
        },
        /**
        * @method: replyComment
        * @description: Show modal reply form
        */
        replyComment() {
            $("#content-topic").addClass("paddingEditorMde");
            $("#mdeReplyModal").show();
        }
    }
});
