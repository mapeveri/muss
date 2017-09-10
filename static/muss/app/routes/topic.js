import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return Ember.RSVP.hash({
            topic: this.get("store").find("topic", params.pk),
        });
    }
});
