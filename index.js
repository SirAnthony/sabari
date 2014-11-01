
var nunjucks = require('nunjucks');
var express = require('express');
var i18n = require('i18n-abide');
var settings = require('./settings.json');
var sabari = require('./lib/sabari.js');
var app = express();

// Localization
app.use(i18n.abide({
	supported_languages: ['en_US', 'ru',],
	default_lang: "en_US",
	translation_directory: "templates/static/i18n",
}));

// Templates setup
var env = nunjucks.configure('templates', {autoescape: true, express: app});

// Routes setup
sabari.init(app);

app.listen(settings.port);
console.log('Server started on port %s', settings.port);
