import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('card-comment', 'Integration | Component | card comment', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{card-comment}}`);

  assert.equal(this.$().text().match(/Reply/), 'Reply');

  // Template block usage:
  this.render(hbs`
    {{#card-comment}}
      template block text
    {{/card-comment}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
