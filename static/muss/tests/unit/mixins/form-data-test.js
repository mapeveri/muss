import EmberObject from '@ember/object';
import FormDataMixin from 'muss/mixins/form-data';
import { module, test } from 'qunit';

module('Unit | Mixin | form data');

// Replace this with your real tests.
test('it works', function(assert) {
  let FormDataObject = EmberObject.extend(FormDataMixin);
  let subject = FormDataObject.create();
  assert.ok(subject);
});
