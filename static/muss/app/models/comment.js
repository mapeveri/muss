import DS from 'ember-data';

export default DS.Model.extend({
    topic: DS.belongsTo('topic'),
    username: DS.attr('string'),
    userPhoto: DS.attr('string'),
    date: DS.attr('string'),
    description: DS.attr('string'),
    totalLikes: DS.attr('number')
});
