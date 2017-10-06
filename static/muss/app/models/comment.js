import DS from 'ember-data';

export default DS.Model.extend({
    topic: DS.belongsTo('topic'),
    user: DS.belongsTo('user'),
    date: DS.attr('string'),
    description: DS.attr('string'),
    markdownDescription: DS.attr(),
    totalLikes: DS.attr('number')
});
