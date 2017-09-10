import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return Ember.RSVP.hash({
            forum: this.get("store").find("forum", params.pk),
            topics: this.get("store").query("topic", {slug: params.slug}),
        });
    }
});
