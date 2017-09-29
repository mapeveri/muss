import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return Ember.RSVP.hash({
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
