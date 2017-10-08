import Route from "@ember/routing/route";
import RSVP from "rsvp";

export default Route.extend({
    model(params) {
        return RSVP.hash({
            topic: this.get("store").query("topic", {pk: params.pk, slug: params.slug, filter: 'only_topic'}).then((topic) => {
                return topic.get("firstObject");
            }),
            comments: this.get("store").query("comment", {topic: params.pk}),
            suggests: this.get("store").query("topic", {suggest: params.pk, filter: 'suggests'}),
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
        * @method redirectoToForum
        * @description: Redirect to route forum
        * @param {*} forum_id
        * @param {*} forum_slug
        */
        redirectoToForum(forum_id, forum_slug) {
            this.transitionTo("forum", forum_id, forum_slug);
        }
    }
});
