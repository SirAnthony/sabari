
var image = require('./image.js')
var _ = require('underscore')
var fs = require('fs')
var path = require('path')
var mime = require('mime')
var crypto = require('crypto')
var settings = require('../settings.json')
var memcached = require('memcached')
var cache = new memcached(settings.memcached, {timeout: 100})

function check_file(filepath, dir, filename){
    var local_name = path.join(dir, filename)
    var type = mime.lookup(filename)
    if (!type.indexOf('image'))
        return image.thumb(filepath, settings.cache_path, settings.cache_url)
    var tname = type.replace('/', '-')
    return {alt: tname, w: 165,
        src: settings.icons_url+'/'+tname+'.png', desc: filename}
}

function prepare(dir, content){
    var directories = []
    var files = []
    var new_thumbs = false
    content.forEach(function(filename, i){
        if (!filename.indexOf('.') && !settings.show_hidden)
            return
	var filepath = path.join(settings.root, dir, filename)
        try { fs.realpathSync(filepath) } 
        catch(e) {
            console.log('Broken path found: '+filepath+': '+e)
            return
        }
	var stat = fs.statSync(filepath)
        var href = path.join(dir, filename)
	if (stat.isDirectory()) {
	    directories.push({
		href: href+'/', src: path.join(settings.icons_url, 'folder.png'),
		alt: 'Folder', desc: filename, w: 165, name: filename
	    });
        } else {
            var data = _.extend({name: filename, href: href},
                check_file(filepath, dir, filename))
            new_thumbs = new_thumbs||data.thumb
            files.push(data)
        }
    })

    var sorter = function(a, b){
        return a.name > b.name ? 1 : a.name < b.name ? -1 : 0 }
    directories.sort(sorter)
    files.sort(sorter)
    var items = directories.concat(files)
    if (dir != '/')
        items.unshift({href: '../', alt: 'Parent',
            src: path.join(settings.icons_url, 'back.png'),
            desc: 'Parent directory', w: 165})
    return {dir: dir, dirs: directories, files: files, items: items, skip: new_thumbs}
}

exports.process = function(dir, callback){
    if (!dir)
        return callback(new Error('Directory not specified'))
    var target = path.join(settings.root, dir)
    var target_real = fs.realpathSync(target)
    if (!fs.existsSync(target_real))
        return callback(new Error('Path not exists: '+dir))
    var stat = fs.statSync(target)
    if (!stat.isDirectory())
        return callback(new Error('Not a directory'))

    var modified = stat.mtime.getTime()
    var hash = crypto.createHash('sha1')
    hash.update(target)
    var cache_key = 'sabari:'+hash.digest('hex')
    cache.get(cache_key, function(err, cached){
        if (err)
            console.log("Memcached error: "+err)
        if (!err && cached && cached.modified == modified)
            return callback(null, cached)
        fs.readdir(target, function(err, files){
            if (err)
                return callback(err)
            var data = prepare(dir, files)
            data.modified = modified
            if (data.skip)
                return callback(null, data)
            return cache.set(cache_key, data, 1000, function(err){
                if (err)
                    console.log("Memcached error: "+err)
                callback(null, data)
            })
        })
    })
}

