import { moduleForComponent, test } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';

moduleForComponent('utils/modal-simple-mde-editor', 'Integration | Component | utils/modal simple mde editor', {
  integration: true
});

test('it renders', function(assert) {

  // Set any properties with this.set('myProperty', 'value');
  // Handle any actions with this.on('myAction', function(val) { ... });

  this.render(hbs`{{utils/modal-simple-mde-editor}}`);

  assert.equal(this.$().text().trim(), '');

  // Template block usage:
  this.render(hbs`
    {{#utils/modal-simple-mde-editor}}
      template block text
    {{/utils/modal-simple-mde-editor}}
  `);

  assert.equal(this.$().text().trim(), 'template block text');
});
