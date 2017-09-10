import Ember from 'ember';

export default Ember.Component.extend({
    isLoading: true,
    model: null,
    submodel: null,
    api: '',
    page: 2,
    store: Ember.inject.service(),
    didInsertElement() {
        let self = this;
        let query = null;
        let pages = null;

        if(self.submodel != null) {
            query = self.model[self.submodel].query;
            pages = self.model[self.submodel].meta.pagination.pages;
        } else {
            query = self.model.query;
            pages = self.model.meta.pagination.pages;
        }

        if(pages == 1) {
            self.set("isLoading", false);
        }

        Ember.$(window).scroll(function () {
            if (Ember.$(window).scrollTop() >= (Ember.$(document).height() - Ember.$(window).height()) - 1) {
                if(self.isLoading) {
                    if(self.page <= pages) {
                        query['page'] = self.page;
                        self.get('store').query(self.api, query).then(function(data) {
                            self.page = self.page + 1;

                            if(self.submodel != null) {
                                self.model[self.submodel].addObjects(data.get("content"));
                            } else {
                                self.model.addObjects(data.get("content"));
                            }

                            if(self.page >= pages) {
                                Ember.$(window).unbind('scroll');
                                setTimeout(() => {
                                    self.set("isLoading", false);
                                }, 500);
                            }
                        });
                    }
                }
            }
         });
    }
});
