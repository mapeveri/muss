import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('reset-password-form', 'Integration | Component | reset password form', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{auth/reset-password-form}}`);

  assert.equal(this.$().text().match(/Email/), 'Email');

  // Template block usage:
  this.render(hbs`
    {{#auth/reset-password-form}}
      template block text
    {{/auth/reset-password-form}}
  `);

  assert.equal(this.$().text().match(/template block text/), 'template block text');
});
