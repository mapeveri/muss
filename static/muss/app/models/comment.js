import DS from 'ember-data';

export default DS.Model.extend({
    topic: DS.belongsTo('topic'),
    //user: DS.belongsTo('user'),
    date: DS.attr('date'),
    description: DS.attr('string'),
    totalLikes: DS.attr('number')
});
