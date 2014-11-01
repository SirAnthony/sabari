
var image = require('./image.js');
var pool = require('./pool.js');
var _ = require('lodash');
var fs = require('fs');
var path = require('path');
var mime = require('mime');
var crypto = require('crypto');
var memcached = require('memcached');
var settings = require('../settings.json');
var cache = new memcached(settings.memcached, {timeout: 100});

var do_thumb = _.bind(image.thumb, image, settings.cache_root, settings.cache_url);
function check_file(dir, filename){
    var local_name = path.join(dir, filename);
    var type = mime.lookup(filename);
    if (!type.indexOf('image') && type.indexOf('djvu')<0){
        var filepath = path.join(settings.root, local_name);
        return do_thumb(filepath);
    }
    var tname = type.replace('/', '-');
    return {alt: tname, w: 165,
        src: settings.icons_url+'/'+tname+'.png', desc: filename};
}

function file_iter(dir, directories, files, filename){
    if (!filename.indexOf('.') && !settings.show_hidden)
        return;
    var filepath = path.join(settings.root, dir, filename);
    try { fs.realpathSync(filepath); }
    catch(e) {
        console.log('Broken path found: '+filepath+': '+e);
        return;
    }
    var stat = fs.statSync(filepath);
    if (stat.isDirectory())
        directories.push({
            href: dir+filename+'/', src: path.join(settings.icons_url, 'folder.png'),
            alt: 'Folder', desc: filename, w: 165, name: filename
        });
    else
        files.push(_.extend({name: filename, href: dir+filename},
            check_file(dir, filename)));
}

var pp = settings.item_per_page;
var sorter = function(a, b){
    return a.name > b.name ? 1 : a.name < b.name ? -1 : 0; };
function slice_items(page, directories, files){
    var sl = 0, count;
    var length = directories.length+files.length;
    if (page>=0){
        count = settings.items_per_page;
        sl = page*count;
        count = Math.min(Math.max(length-sl, 0), count);
    } else
        count = length;
    var array = new Array(count), i=0;
    while(sl<directories.length && i<count)
        array[i++] = directories[sl++];
    sl -= directories.length;
    while(i<count&&sl<files.length)
        array[i++] = files[sl++];
    return array;
}

var parent_dir = {
    href: '../', alt: 'Parent', desc: 'Parent directory', w: 165,
    src: path.join(settings.icons_url, 'back.png')
};
function is_skip(item){
    return item.thumb; }
function prepare(dir, content, page){
    var directories = [];
    var files = [];
    content.forEach(_.bind(file_iter, null, dir, directories, files));
    directories.sort(sorter);
    files.sort(sorter);
    if (dir != '/')
        directories.unshift(parent_dir);
    var items = slice_items(page, directories, files);
    return {dir: dir, dirs: directories, files: files,
        items: items, skip: _.some(items, is_skip)};
}

function memcached_err(err, data, next){
    if (err)
        console.log("Memcached error: "+err);
    if (next)
        next.call(null, err, data);
}

function check_path(dir){
    if (!dir)
        throw new Error('Directory not specified');
    var target = path.join(settings.root, dir);
    var target_real = fs.realpathSync(target);
    if (!fs.existsSync(target_real))
        throw new Error('Path not exists: '+dir);
    return target;
}

function check_page(page){
    if (typeof page != 'number')
        page = parseInt(page)||0;
    if (page<0)
        page = -1;
    return page;
}

function err404(err){
    err = err||new Error('Page not found');
    err.status = 404;
    return err;
}

exports.process = function(dir, page, callback){
    var target;
    try { target = check_path(dir); }
    catch (err) { return callback(err404(err)); }
    var stat = fs.statSync(target);
    if (!stat.isDirectory())
        return callback(new Error('Not a directory'));
    page = check_page(page);
    var modified = stat.mtime.getTime();
    var hash = crypto.createHash('sha1').update(target).digest('hex');
    var fs_key = 'sabari:fs:'+hash;
    var cache_key = 'sabari:'+hash+':'+page;
    pool.chain([['get', cache, cache_key], memcached_err,
    function(err, cached, next){
        if (cached && cached.modified == modified)
            return callback(null, cached);
        next();
    }, ['get', cache, fs_key], memcached_err,
    function(err, cached, next){
        if (cached && cached.modified == modified)
            return next(null, cached);
        pool.chain([['readdir', fs, target],
        function(err, files, subnext){
            if (!err)
                subnext(files, 1000);
            next(err, files);
        }, ['set', cache, fs_key], memcached_err]);
    }, function(err, files, next){
        if (err)
            return callback(err);
        if (pp*page>files.length)
            return callback(err404());
        var prep = prepare(dir, files, page);
        var data = {modified: modified, page: page,
            items: prep.items, dir: prep.dir,
            length: prep.dirs.length+prep.files.length};
        if (!prep.skip)
            next(data, 1000);
        callback(null, data);
    }, ['set', cache, cache_key], memcached_err]);
};

