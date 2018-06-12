import Component from '@ember/component';
import { inject as service} from '@ember/service';
import $ from 'jquery';

export default Component.extend({
    isLoading: true,
    model: null,
    submodel: null,
    api: '',
    page: 2,
    store: service('store'),

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

        $(window).scroll(() => {
            if ($(window).scrollTop() >= ($(document).height() - $(window).height()) - 1) {
                if(self.isLoading) {
                    if(self.page <= pages) {
                        query['page'] = self.page;
                        self.page = self.page + 1;
                        self.get('store').query(self.api, query).then((data) => {
                            if(self.submodel != null) {
                                data.get("content").forEach((item) => {
                                    self.model[self.submodel].content.pushObject(item);
                                });
                            } else {
                                data.get("content").forEach((item) => {
                                    self.model.content.pushObject(item);
                                });
                            }

                            if(self.page >= pages) {
                                $(window).unbind('scroll');
                                try{
                                    self.set("isLoading", false);
                                } catch(e) {
                                    // Ignore
                                }
                            }
                        });
                    }
                }
            }
         });
    }
});
