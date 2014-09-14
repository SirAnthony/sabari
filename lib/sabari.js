
var express = require('express')
var fs = require('fs')
var path = require('path')
var settings = require('../settings.json')
var pkg = require('../package.json')
var crypto = require('crypto')
var _ = require('underscore')
var directory = require('./directory.js')

function default_route(req, res, next){
    res.status(404)
    if (req.accepts('html'))
        res.render_context('404.html', {url: req.url})
    else if (req.accepts('json'))
        res.send({error: req.gettext('Not found')})
    else
        res.type('txt').send(req.gettext('Not found'))
}

var elapsed_time = function(start){
    var elapsed = process.hrtime(start)
    return elapsed[0]+elapsed[1]/1000000000
}

exports.init = function(app){
    app.use(settings.static_url, express.static(
        path.join(__dirname, '..', 'static')))

    // Context
    app.use(function(req, res, next){
        var start = process.hrtime()
	res.context = {NOTIFICATIONS: settings.notifications, 
            VERSION: pkg.version, STATIC_URL: settings.static_url}
	res.render_context = function(template, data){
            var elapsed = elapsed_time(start)
	    var context_data = _.extend({time: elapsed}, res.context, data)
	    res.render(template, context_data)
	}
        res.render_default = function(err, data){
            if (err){
                res.status = 500
                res.render_context('500.html', {error: err.message})
            } else {
                res.status = 200
                res.render_context('index.html', data)
            }
        }
        res.render_error = function(error){
            res.status = 500
            if (req.accepts('html'))
                res.render_context('500.html', {error: error})
            else
                res.send({error: error})
        }
        next()
    })

    app.use(function(req, res, next){
        try { directory.process(unescape(req.path), res.render_default) }
        catch(e){ res.render_error(e) }
    })

    app.use(default_route)
}

