import Route from "@ember/routing/route";
import RSVP from "rsvp";

export default Route.extend({
    model() {
        return RSVP.hash({
            forums: this.get("store").query("category", {filter: 'forums'}),
            topics: this.get("store").query("topic", {filter: 'latest'})
        });
    }
});
