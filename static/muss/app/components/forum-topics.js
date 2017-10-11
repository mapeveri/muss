import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { isPresent } from "@ember/utils";
import $ from 'jquery';
import config from './../config/environment';
import { gettextHelper } from '../helpers/gettext';

export default Component.extend({
    store: service('store'),
    session: service('session'),
    router: service('-routing'),
    ajax: service('ajax'),
    currentUser: service('current-user'),
    currentUrl: window.location.href,
    rssUrl: config.APP.API_HOST + "/" + "feed/",
    isLoaded: false,
    userLogin: null,
    canCreateTopic: false,
    canRegister: false,
    isAdminOrModerator: false,
    addTopicField: '',
    addTopicTitle: '',
    enableAddTopic: function() {
        return !isPresent(this.addTopicField) || !isPresent(this.addTopicTitle);
    }.property('addTopicField', 'addTopicTitle'),

    didInsertElement() {
        this._super();

        if (this.get('session.isAuthenticated')) {
            let user_login = parseInt(this.get('currentUser').user.id);
            this.set('userLogin', user_login);
        }

        this.checkPermissionsUser();
    },
    /**
    * @method FinishedLoading
    * @description: Finished loading data server and hide loading
    */
    FinishedLoading() {
        //Is completed
        this.set('isLoaded', true);
    },
    /**
    * @method checkPermissionsUser
    * @description: Check if user logged can create topic or register, etc.
    */
    checkPermissionsUser(){
        let publicForum = this.get('model.forum.publicForum');
        let isAuthenticated = this.get('session.isAuthenticated');
        if (isAuthenticated) {

            // If is a public forum, not check permissions
            if(publicForum) {
                this.set('canCreateTopic', true);
                //Is completed
                this.FinishedLoading();
                return;
            }

            let namespace = config.APP.API_NAMESPACE;
            let pk = this.get('session').session.content.authenticated.user.id;

            //Check if user logged is superuser
            let isSuperUser = this.get('session').session.content.authenticated.user.is_superuser;

            return this.get('ajax').request('/' + namespace + '/check-permissions-forum-user/', {
                method: 'GET',
                data: {'user_id': pk, 'forum_id': this.model.forum.id}
            }).then(response => {
                //Is completed
                this.FinishedLoading();

                let isRegistered = response.data.register;
                let isModerator = response.data.is_moderator;
                let isTroll = response.data.is_troll;

                this.set('isAdminOrModerator', isSuperUser || isModerator);

                //Check if is a troll
                if(!isTroll) {
                    //Check if user logged can create topic
                    if(isRegistered || isModerator || isSuperUser) {
                        this.set('canCreateTopic', true);
                    }

                    //Check if user logged can register or unregister
                    if(isRegistered) {
                        //Already register
                        this.set('canRegister', false);
                    } else {
                        if(!isModerator || !isSuperUser ) {
                            this.set('canRegister', true)
                        }
                    }
                }
            });
        } else {
            //Is completed
            this.FinishedLoading();
        }
    },
    actions: {
        /**
        * @method registerUser
        * @description: Register user in forum
        */
        registerUser() {
            this.get('store').find('user', this.userLogin).then((user) => {
                let register = this.get('store').createRecord('register', {
                    'forum': this.model.forum,
                    'user': user
                });

                register.save().then(() => {
                    this.set('canRegister', false);
                    this.set('canCreateTopic', true);
                }).catch(() => {
                    window.toastr.error(gettextHelper("Failed to register"))
                });
            });
        },
        /**
        * @method unRegisterUser
        * @description: Remove register user in forum
        */
        unRegisterUser() {
            this.get('store').query('register', {'user': this.userLogin, 'forum': this.model.forum.id, 'filter': 'get_register'}).then((register_aux) => {
                let register = register_aux.get("firstObject");
                register.destroyRecord().then(() => {
                    this.set('canRegister', true);
                    this.set('canCreateTopic', false);
                });
            }).catch(() => {
                window.toastr.error(gettextHelper("Failed to unregister"))
            })
        },
        /**
        * @method showAddTopic
        * @description: Show modal editor mde
        */
        showAddTopic() {
            //Show modal editor
            $("#mdeAddTopicModal").addClass('mde-modal-content-open').height(350).trigger("open");
        },
        /**
        * @method createTopic
        * @description: Add new topic
        */
        createTopic() {
            this.get('store').find('user', this.userLogin).then((user) => {
                let addTopic = this.get('store').createRecord('topic', {
                    'user': user,
                    'forum': this.model.forum,
                    'title': this.addTopicTitle,
                    'description': this.addTopicField
                });

                addTopic.save().then((topic) => {
                    setTimeout(() => {
                        let router = this.get('router');
                        router.router.transitionTo('topic', topic.id, topic.get('slug'));
                    }, 500);
                });
            });
        }
    }
});
