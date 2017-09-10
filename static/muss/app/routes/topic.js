import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return Ember.RSVP.hash({
            topic: this.get("store").find("topic", params.pk),
            comments: this.get("store").query("comment", {topic: params.pk}),
            suggests: this.get("store").query("topic", {suggest: params.pk}),
        });
    }
});
