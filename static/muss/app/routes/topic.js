import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return Ember.RSVP.hash({
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
    }
});
