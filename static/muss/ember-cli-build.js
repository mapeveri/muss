/* eslint-env node */
'use strict';

const EmberApp = require('ember-cli/lib/broccoli/ember-app');

module.exports = function(defaults) {
    let app = new EmberApp(defaults, {
    // Add options here
    });

    // Use `app.import` to add additional libraries to the generated
    // output files.
    //
    // If you need to use different assets in different
    // environments, specify an object as the first parameter. That
    // object's keys should be the environment name and the values
    // should be the asset to use in that environment.
    //
    // If the library that you are including contains AMD or ES6
    // modules that you would like to import into your application
    // please specify an object with the list of modules as keys
    // along with the exports of each module as its value.

    app.import("vendor/styles.css");
    app.import("bower_components/toastr/toastr.min.css");
    app.import("bower_components/toastr/toastr.min.js");
    app.import("node_modules/simplemde/dist/simplemde.min.js");
    app.import("node_modules/simplemde/dist/simplemde.min.css");

    const dirFontsSemantic = 'node_modules/semantic-ui-css/themes/default/assets/fonts/';
    app.import(`${dirFontsSemantic}brand-icons.eot`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}brand-icons.svg`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}brand-icons.ttf`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}brand-icons.woff`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}brand-icons.woff2`, {destDir: '/assets/themes/default/assets/fonts'});

    app.import(`${dirFontsSemantic}outline-icons.eot`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}outline-icons.svg`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}outline-icons.ttf`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}outline-icons.woff`, {destDir: '/assets/themes/default/assets/fonts'});
    app.import(`${dirFontsSemantic}outline-icons.woff2`, {destDir: '/assets/themes/default/assets/fonts'});

    return app.toTree();
};
