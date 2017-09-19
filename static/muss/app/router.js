import Ember from 'ember';
import config from './config/environment';

const Router = Ember.Router.extend({
    location: config.locationType,
    rootURL: config.rootURL
});

Router.map(function() {
  this.route('index', { path: '/' });
  this.route('forum', { path: '/forum/:pk/:slug' });
  this.route('topic', { path: '/topic/:pk/:slug' });
  this.route('logout');
});

export default Router;
