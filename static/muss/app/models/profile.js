import DS from 'ember-data';

export default DS.Model.extend({
    user: DS.belongsTo('user'),
    profile: DS.attr('string'),
    about: DS.attr('string'),
    photo: DS.attr(),
    location: DS.attr('string'),
    isTroll: DS.attr('boolean'),
});
