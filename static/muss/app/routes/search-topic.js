import Route from "@ember/routing/route";

export default Route.extend({
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
