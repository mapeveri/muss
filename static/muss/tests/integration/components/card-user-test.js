import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('card-user', 'Integration | Component | card user', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{card-user}}`);

  assert.equal(this.$().text().match(/Online/), 'Online');

  // Template block usage:
  this.render(hbs`
    {{#card-user}}
      template block text
    {{/card-user}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
