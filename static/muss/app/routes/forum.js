import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import RSVP from "rsvp";

export default Route.extend({
    ajax: service('ajax'),
    model(params) {

        return RSVP.hash({
            forum: this.get("store").query("forum", {pk: params.pk, slug: params.slug, filter: "only"}).then((forum) => {
                return forum.get("firstObject");
            }),
            topics: this.get("store").query("topic", {slug: params.slug, filter: "by_forum"}),
            messages: this.get('ajax').request('/messageforums/', {
                method: 'GET',
                data: {
                    forum: params.pk
                }
            }).then(response => {
                return response.data;
            })
        });
    },
    afterModel(model) {
        //Check if find forum
        if (model.forum == undefined) {
            this.transitionTo('index');
        }
    }
});
