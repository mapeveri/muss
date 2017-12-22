import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('categories-forums', 'Integration | Component | categories forums', {
  integration: true
});

test('it renders', function(assert) {

    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.on('myAction', function(val) { ... });

    window.muss = {};
    window.muss.site_name = "Test muss";
    this.render(hbs`{{categories-forums}}`);

    assert.equal(this.$().text().match(/Forums/), 'Forums');

    // Template block usage:
    this.render(hbs`
        {{#categories-forums}}
        template block text
        {{/categories-forums}}
    `);

    assert.equal(this.$().text().match(/template block text/), 'template block text');
});
