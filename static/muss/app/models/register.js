import DS from 'ember-data';

export default DS.Model.extend({
    forum: DS.belongsTo('forum'),
    user: DS.belongsTo('user'),
    date: DS.attr(),
});
