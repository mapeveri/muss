import DS from 'ember-data';

export default DS.Model.extend({
    username: DS.attr('string'),
    email: DS.attr('string'),
    firstName: DS.attr('string'),
    lastName: DS.attr('string'),
    userPhoto: DS.attr('string'),
    isActive: DS.attr('boolean'),
    isSuperUser: DS.attr('boolean'),
});
