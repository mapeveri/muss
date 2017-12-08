import Component from '@ember/component';
import { inject as service} from '@ember/service';
import { setTitlePage } from '../libs/utils';

export default Component.extend({
    router: service('-routing'),

    didInsertElement() {
        this._super();

        //Update title page html
        setTitlePage(window.muss.site_name);

        //If only has one forum redirect
        let forums = this.get('model.forums').filterBy('isHeader', false);
        if(forums.length == 1) {
            let forum = forums[0];
            let pk = forum.get('pk');
            let slug = forum.get('slug');

            //Redirect to forum
            let router = this.get('router');
            router.router.transitionTo('forum', pk, slug);
        }
    }
});
