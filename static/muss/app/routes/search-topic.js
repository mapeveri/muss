import Ember from 'ember';

export default Ember.Route.extend({
    model(params) {
        return this.get("store").query("topic", {title: params.q, filter: 'search'});
    },
    actions: {
        queryParamsDidChange() {
          // opt into full refresh
          this.refresh();
        }
    }
});
