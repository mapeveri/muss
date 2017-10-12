import TextField from "@ember/component/text-field"

export default TextField.extend({
    id: '',
    name: '',
    value: null,

    init() {
        this._super(...arguments);
    },
    didInsertElement() {
        this._super();
        var options = {
            types: ['(regions)']
        };

        setTimeout(() => {
            var input = document.getElementById(this.get('id'));
            var autocomplete = new window.google.maps.places.Autocomplete(input , options);
            autocomplete.addListener('place_changed', () => {
                var place = autocomplete.getPlace();
                this.set('value', place.formatted_address);
            });
        }, 1000);
    }
});
