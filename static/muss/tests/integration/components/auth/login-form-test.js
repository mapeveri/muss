import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('auth/login-form', 'Integration | Component | auth/login form', {
  integration: true
});

test('it renders', function(assert) {

    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.on('myAction', function(val) { ... });

    this.render(hbs`{{auth/login-form}}`);

    assert.equal(this.$().text().match(/Log in/), 'Log in');

    // Template block usage:
    this.render(hbs`
        {{#auth/login-form}}
        template block text
        {{/auth/login-form}}
    `);

    assert.equal(this.$().text().match(/template block text/), 'template block text');
});
