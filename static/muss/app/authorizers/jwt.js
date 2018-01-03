import Ember from 'ember';
import { isEmpty } from '@ember/utils';
import { inject as service} from '@ember/service';
import Base from 'ember-simple-auth/authorizers/base';

export default Base.extend({
    session: service('session'),

    authorize(data, block) {
        if (Ember.testing) {
            block('Authorization', 'jwt beyonce');
        }
        const { token } = data
        if (this.get('session.isAuthenticated') && !isEmpty(token)) {
            block('Authorization', `jwt ${token}`);
        }
    }
});
