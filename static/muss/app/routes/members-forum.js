import Route from "@ember/routing/route";
import RSVP from "rsvp";

export default Route.extend({
    model(params) {
        return RSVP.hash({
            users: this.get("store").query("register", {forum: params.pk, filter: "members"}),
            forum: this.get("store").query("forum", {pk: params.pk, slug: params.slug, filter: "only"}).then((forum) => {
                return forum.get("firstObject");
            }),
        });
    },
});
