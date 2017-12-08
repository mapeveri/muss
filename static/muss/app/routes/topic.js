import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import RSVP from "rsvp";

export default Route.extend({
    session: service('session'),
    currentUser: service('current-user'),

    model(params) {
        //Get user logged
        let user_login;
        if (this.get('session.isAuthenticated')) {
            user_login = parseInt(this.get('currentUser').user.id);
        } else {
            user_login = null;
        }

        return RSVP.hash({
            topic: this.get("store").query("topic", {pk: params.pk, slug: params.slug, filter: 'only_topic'}).then((topic) => {
                return topic.get("firstObject");
            }),
            comments: this.get("store").query("comment", {topic: params.pk}),
            suggests: this.get("store").query("topic", {suggest: params.pk, filter: 'suggests'}).catch(() => {}),
            profile: (user_login != undefined ? this.get("store").find('user', user_login).then((user) => {
                return user.get('user').then((profile) => {
                    return profile;
                });
            }).catch(() => {
                return false;
            }) : false)
        });
    },
    afterModel(model) {
        //Check if find topic
        if (model.topic == undefined) {
            this.transitionTo('index');
        }
    },
    actions: {
        /**
        * @method redirectToForum
        * @description: Redirect to route forum
        * @param {*} forum_id
        * @param {*} forum_slug
        */
        redirectToForum(forum_id, forum_slug) {
            this.transitionTo("forum", forum_id, forum_slug);
        }
    }
});
