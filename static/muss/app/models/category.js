import DS from 'ember-data';

export default DS.Model.extend({
    name: DS.attr('string'),
    categoryId: DS.attr('number'),
    parentId: DS.attr('number'),
    description: DS.attr('string'),
    topicsCount: DS.attr('number'),
    hidden: DS.attr('boolean'),
    isHeader: DS.attr('boolean'),
    pk: DS.attr('number'),
    slug: DS.attr('string'),
    forums: DS.hasMany('forum'),
});
