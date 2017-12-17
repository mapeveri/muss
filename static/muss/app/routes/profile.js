import Route from "@ember/routing/route";
import { inject as service} from '@ember/service';
import RSVP from "rsvp";
import config from './../config/environment';

export default Route.extend({
    ajax: service('ajax'),
    model(params) {
        let namespace = config.APP.API_NAMESPACE;

        return RSVP.hash({
            profile: this.get("store").query("profile", {username: params.username, filter: "get_profile_username"})
            .then((profile) => {
                return profile.get("firstObject");
            })
            .catch(() => {
                this.transitionTo('index');
            }),
            topics: this.get("store").query("topic", {username: params.username, filter: "by_user"}),
            forums: this.get('ajax').request('/' + namespace + '/forums-by-user/', {
                method: 'GET',
                data: {
                    username: params.username
                }
            }).then(response => {
                return response.data;
            })
        });
    }
});
