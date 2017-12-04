import DS from 'ember-data';

export default DS.Model.extend({
    idObject: DS.attr('number'),
    user: DS.belongsTo('user'),
    isSeen: DS.attr('boolean'),
    date: DS.attr('string'),
    comment: DS.attr(),
    topic: DS.attr(),
    register: DS.attr(),
});
