
var express = require('express');
var fs = require('fs');
var path = require('path');
var settings = require('../settings.json');
var pkg = require('../package.json');
var crypto = require('crypto');
var _ = require('lodash');
var directory = require('./directory.js');

function default_route(req, res, next){
    res.status(404);
    if (req.accepts('html'))
        res.render_context('404.html', {url: req.url});
    else if (req.accepts('json'))
        res.send({error: req.gettext('Not found')});
    else
        res.type('txt').send(req.gettext('Not found'));
}

var elapsed_time = function(start){
    var elapsed = process.hrtime(start);
    return elapsed[0]+elapsed[1]/1000000000;
};

var pp = settings.items_per_page;
function paginate(data){
    var pages = data.pages = Math.ceil(data.length/pp);
    if (pages<2)
        data.page = -1;
    var page = data.page;
    if (data.length && page>=0){
        data.pmin = Math.max(0, page-3);
        data.pmax = Math.min(page+3, pages);
    }
    return data;
}

exports.init = function(app){
    app.use(settings.static_url, express.static(
        path.join(__dirname, '..', 'static')));
    app.use(settings.cache_url, express.static(settings.cache_root));
    app.use(settings.icons_url, express.static(settings.icons_root));

    // Context
    app.use(function(req, res, next){
        var start = process.hrtime();
        res.context = {NOTIFICATIONS: settings.notifications,
            VERSION: pkg.version, STATIC_URL: settings.static_url,
            columns: settings.items_columns};
	res.render_context = function(template, data){
            paginate(data);
            var elapsed = elapsed_time(start);
	    var context_data = _.extend({time: elapsed}, res.context, data);
	    res.render(template, context_data);
	};
        res.render_json = function(err, data){
            if (err)
                return res.send({response: 'error', error: err.message});
            res.send({response: 'data', data: paginate(data)});
        };
        res.render_default = function(err, data){
            if (err){
                res.status = err.status||500;
                res.render_context(res.status+'.html', {error: err.message});
            } else {
                res.status = 200;
                res.render_context('index.html', data);
            }
        };
        res.render_error = function(error){
            res.status = 500;
            if (req.accepts('html'))
                res.render_context('500.html', {error: error});
            else
                res.send({error: error});
        };
        next();
    });

    app.use(function(req, res, next){
        var json = req.param('json');
        var renderer = json ? res.render_json : res.render_default;
        try { directory.process(unescape(req.path), req.param('p'), renderer); }
        catch(err){ 
            var reporter = json ? res.render_json : res.render_error;
            reporter(err);
        }
    });

    app.use(default_route);
};

