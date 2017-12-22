import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('auth/signup-form', 'Integration | Component | auth/signup form', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{auth/signup-form}}`);

  assert.equal(this.$().text().match(/Sign up/), 'Sign up');

  // Template block usage:
  this.render(hbs`
    {{#auth/signup-form}}
      template block text
    {{/auth/signup-form}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
