import DS from 'ember-data';

export default DS.Model.extend({
    name: DS.attr('string'),
    slug: DS.attr('string'),
    category: DS.belongsTo('category'),
    parent: DS.belongsTo('forum'),
    parentsForums: DS.attr(),
    childsForums: DS.attr(),
    description: DS.attr('string'),
    date: DS.attr('date'),
    topicsCount: DS.attr('number'),
    hidden: DS.attr('boolean'),
    isModerate: DS.attr('boolean'),
    messagesForums: DS.hasMany('message-forum'),
    topics: DS.hasMany('topic')
});
