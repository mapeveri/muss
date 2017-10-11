import Route from "@ember/routing/route";
import RSVP from "rsvp";

export default Route.extend({
    model(params) {
        return RSVP.hash({
            profile: this.get("store").find("profile", params.username).catch(() => {
                this.transitionTo('index');
            }),
            topics: this.get("store").query("topic", {username: params.username, filter: "by_user"}),
        });
    }
});
