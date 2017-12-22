import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('utils/loading-spinner', 'Integration | Component | utils/loading spinner', {
  integration: true
});

test('it renders', function(assert) {
  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{utils/loading-spinner}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#utils/loading-spinner}}
      template block text
    {{/utils/loading-spinner}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
