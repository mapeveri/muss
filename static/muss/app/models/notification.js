import DS from 'ember-data';

export default DS.Model.extend({
    idObject: DS.attr('number'),
    idUser: DS.attr('number'),
    isSeen: DS.attr('boolean'),
    date: DS.attr('date')
});
