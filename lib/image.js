
var fs = require('fs')
var path = require('path')
var crypto = require('crypto')
var easyimg = require('easyimage')
var touch = require('touch')
var pool = require('./pool.js').Pool

var extensions = {'JPEG': '.jpg', 'PNG': '.png',
    'GIF': '.gif', 'TIFF': '.tiff'}

exports.thumb = function(filepath, cache_path, cache_url){
    var hash = crypto.createHash('sha1')
    hash.update(filepath)
    hash = hash.digest('hex')
    var dstpath = path.join(cache_path, hash)
    for (var type in extensions){
        var ext = extensions[type]
        if (fs.existsSync(dstpath+ext))
            return {hash: hash, src: cache_url+'/'+hash+ext}
    }
    if (!fs.existsSync(dstpath+'.lock'))
        pool.add(function(resolve){
            generate_thumb(filepath, dstpath, resolve) })
    return {desc: 'Thumbinal creation', thumb: true}
}



function generate_thumb(filepath, dstpath, resolve){
    var maxsize = 200
    touch.sync(dstpath+'.lock')
    var error_catcher = function(e){
        fs.unlink(dstpath+'.lock')
        console.log('Thumbinal creation error for "'+filepath
                +'": '+e.message+'\nStack:\n'+e.stack)
        return resolve(e)
    }
    return easyimg.info(filepath).then(function(img){
        var format = 'JPEG'
        if (Object.keys(extensions).indexOf(img.type)>=0)
            format = img.type
        var w = img.width, h = img.height
        var wmult = h>w ? (w/h) : 1
        var hmult = h>w ? 1 : h/w
        if (h > w){
            w = (w/h)*maxsize
            h = maxsize
        } else {
            h = (h/w)*maxsize
            w = maxsize
        }
        return easyimg.thumbnail({
            src: filepath, dst: dstpath+extensions[format],
            width: wmult*maxsize, height: hmult*maxsize,
        }).then(function(f){
            fs.unlink(dstpath+'.lock') 
            return resolve(null, f)
        }).catch(error_catcher)
    }).catch(error_catcher)
}
