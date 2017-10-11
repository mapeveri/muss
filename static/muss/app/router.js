import Router from "@ember/routing/router";
import config from './config/environment';

const router = Router.extend({
    location: config.locationType,
    rootURL: config.rootURL
});

router.map(function() {
  this.route('index', { path: '/' }, () => {
      this.route('forum', { path: '/forum/:pk/:slug' });
      this.route('members-forum', { path: '/members-forum/:pk/:slug' });
      this.route('search-topic', { path: '/search/'});
      this.route('topic', { path: '/topic/:pk/:slug' });
      this.route('logout');
  });
  this.route('confirm-email', { path: '/confirm-email/:username/:activation_key' });
  this.route('reset-password');
  this.route('reset', { path: '/reset/:uidb64/:token'});

  this.route('404', { path: '/*path' });
});

export default router;
