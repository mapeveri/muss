import Component from '@ember/component';
import { computed } from '@ember/object';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import { closeAllEditor, showModalLogin } from '../libs/utils';

export default Component.extend({
    ajax: service('ajax'),
    session: service('session'),
    currentUser: service('current-user'),
    isCreatorComment: false,
    userLogin: null,
    commentId: null,
    showLike: true,
    contentEdit: '',
    enableContentEdit: computed('contentEdit', {
        get() {
            return !isPresent(this.contentEdit);
        }
    }),

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

            //Set comment id
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
                this.get('ajax').request('/likecomments/', {
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
            this.get('ajax').request('/likecomments/' + this.commentId + '/', {
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
        * @method replyComment
        * @description: Show modal reply form
        */
        replyComment() {
            if(this.get('session.isAuthenticated')) {
                //If exists other editor mde opened, when close all
                closeAllEditor();
                //Show modal editor
                $("#mdeReplyModal").addClass('mde-modal-content-open').height(300).trigger("open");
            } else {
                showModalLogin();
            }
        },
        /**
        * @method showEditComment
        * @description: Show edit modal comment
        */
        showEditComment() {
            //If exists other editor mde opened, when close all
            closeAllEditor();

            //Display editor mde for edit comment
            let commentId = this.get('comment.id');
            let contentComment = this.get('comment.description');
            $("#mdeEditModal_" + commentId).addClass('mde-modal-content-open').height(300).trigger("open");
            this.set('contentEdit', contentComment);
        },
        /**
        * @method editComment
        * @description: Save in db the edit comment
        */
        editComment() {
            let commentId = this.get('comment.id');
            this.comment.set('description', this.contentEdit);
            this.comment.save().then(() => {
                $("#mdeEditModal_" + commentId).removeClass('mde-modal-content-open').height(0).trigger("close");
            });
        }
    }
});
