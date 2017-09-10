import DS from 'ember-data';

export default DS.Model.extend({
    forum: DS.belongsTo('forum'),
    messageInformation: DS.attr('string'),
    messageExpiresFrom: DS.attr('date'),
    messageExpresTo: DS.attr('date'),
});
