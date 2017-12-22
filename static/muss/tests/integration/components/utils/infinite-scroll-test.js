import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('infinite-scroll', 'Integration | Component | infinite scroll', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{utils/infinite-scroll}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#utils/infinite-scroll}}
      template block text
    {{/utils/infinite-scroll}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
