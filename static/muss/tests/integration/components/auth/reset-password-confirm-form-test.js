import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('reset-password-confirm-form', 'Integration | Component | reset password confirm form', {
  integration: true
});

test('it renders', function(assert) {

    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.on('myAction', function(val) { ... });
    this.render(hbs`{{auth/reset-password-confirm-form}}`);

    assert.equal(this.$().text().trim(), '');

    // Template block usage:
    this.render(hbs`
        {{#auth/reset-password-confirm-form}}
        template block text
        {{/auth/reset-password-confirm-form}}
    `);

    assert.equal(this.$().text().trim(), 'template block text');
});
