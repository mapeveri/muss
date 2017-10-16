import DS from 'ember-data';

export default DS.Model.extend({
    username: DS.attr('string'),
    email: DS.attr('string'),
    firstName: DS.attr('string'),
    password: DS.attr('string'),
    lastName: DS.attr('string'),
    userPhoto: DS.attr('string'),
    isActive: DS.attr('boolean'),
    isSuperUser: DS.attr('boolean'),
    topics: DS.hasMany('topic'),
    comments: DS.hasMany('comment'),
    registers: DS.hasMany('register'),
    moderators: DS.hasMany('forum'),
    profile: DS.belongsTo('profile'),
    notifications: DS.hasMany('notification'),
});
