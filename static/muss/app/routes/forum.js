import Route from "@ember/routing/route";
import RSVP from "rsvp";

export default Route.extend({
    model(params) {
        return RSVP.hash({
            forum: this.get("store").query("forum", {pk: params.pk, slug: params.slug}).then((forum) => {
                return forum.get("firstObject");
            }),
            topics: this.get("store").query("topic", {slug: params.slug, filter: "by_forum"}),
        });
    },
    afterModel(model) {
        //Check if find forum
        if (model.forum == undefined) {
            this.transitionTo('index');
        }
    }
});
