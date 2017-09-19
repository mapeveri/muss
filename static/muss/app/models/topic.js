import DS from 'ember-data';

export default DS.Model.extend({
    forum: DS.belongsTo('forum'),
    //user: DS.belongsTo('user'),
    userPhoto: DS.attr('string'),
    username: DS.attr('string'),
    slug: DS.attr('string'),
    title: DS.attr('string'),
    date: DS.attr(),
    lastActivity: DS.attr(),
    description: DS.attr('string'),
    attachment: DS.attr('string'),
    idAttachment: DS.attr('string'),
    isClose: DS.attr('boolean'),
    isModerate: DS.attr('boolean'),
    isTop: DS.attr('boolean'),
    totalLikes: DS.attr('number'),
    views: DS.attr('number'),
    totalComments: DS.attr('number'),
    topics: DS.hasMany('comment'),
});
