

define(['lib/element'], function(L){

function RequestProcessor(parsers, caller){
    this.parsers = parsers;
    this.caller = caller||this;
}
var R = RequestProcessor.prototype;
R.prepare = function(){};
R.message = function(msg, type){};
R.ready = function(xhr, state){ return true; };
R.catch$ = function(){};
R.done = function(xhr, func){
    return this._process.bind(this, xhr, func||this.parse); };
R.processed = function(){};
R._process = function(xhr, done){
    try {
        if (!this.ready(xhr.readyState, xhr))
            return;
        if (xhr.readyState == 4)
            done.call(this, xhr.responseText, xhr.status);
    } catch(e){ this.catch$(e); }
};
R.parse = function(resp, status){
    if (status>399 && status<600)
        throw new Error('Server return status '+status);
    // way to pass functions
    // resp = resp.replace(/"\$(.+?)\$"/gi, '$1');
    resp = JSON.parse(resp);
    if(resp.response == 'error')
        throw new Error(resp.text||'Unknown error.');
    else {
        var parser = this.parsers[resp.response];
        if(!parser)
            throw new Error('Unexpected response type: '+resp.response);
        parser.call(this.caller, resp);
    }
    this.processed();
};

var Ajax = function(prefix){
    this.url_prefix = prefix||''; };
var A = Ajax.prototype;
Ajax.processor = RequestProcessor;
var _defaultProcessor = new RequestProcessor({});

var activex = ['Msxml2.XMLHTTP', 'Microsoft.XMLHTTP', 'Msxml2.XMLHTTP.4.0'];
function xmlhttp(){
    if (window.XMLHttpRequest)
        return new XMLHttpRequest();
    for (var i=0; i<activex.length; ++i){
        var xhr;
        try { xhr = new ActiveXObject(activex[i]); }
        catch (e) { continue; }
        activex = [activex[i]];
        return xhr;
    }
}

function post_data(boundary, name, value){
    var crlf = '\r\n';
    var s = '--' + boundary + crlf;
    s += 'Content-Disposition: form-data; name="' + name + '"';
    // isFile
    if (value !== null && typeof value === "object" &&
            'lastModifiedDate' in value && 'name' in value){
        s += '; filename="' + value.name + '"' + crlf;
        s += 'Content-Type: application/octet-stream' + crlf;
        var reader = new FileReader();
        reader.readAsBinaryString(value);
        s += crlf + reader.result + crlf;
    } else {
        s += crlf + crlf + (L.isString(value) ? value :
            JSON.stringify(value)) + crlf;
    }
    return s;
}

function post_request(url, qry, opts){
    var bnd = '-----------' + parseInt(Math.random()*1000000000000);
    var k = Object.keys(qry);
    var request = '';
    Objects.keys(qry).forEach(function(item){
        var q = qry[item];
        if(!q) return;
        if(L.isArray(q)){
            for(var j=0; j<q.length; j++)
                request += post_data(bnd, item, q[j]);
        } else
            request += post_data(bnd, item, q);
    });
    request += '--'+boundary+'--';
    return {request: request, boundary: bnd, headers: {
        'Content-type': 'multipart/form-data; boundary='+bnd}};
}

function get_request(url, qry, opts){
    var keys = Object.keys(qry);
    var uri = keys.length ? '?' : '';
    for (var k=0; k<keys.length; ++k)
        uri += (k>0?'&':'')+keys[k]+'='+encodeURIComponent(qry[keys[k]]);
    return {request: null, uri: uri};
}

function put_request(url, qry, opts){
    var d = get_request(url, qry, opts);
    return {request: opts.data, uri: d.uri};
}

var REQUESTS = {
    GET: get_request,
    POST: post_request,
    PUT: put_request,
};

A.load = function(url, qry, opts){
    var processor = opts.processor||_defaultProcessor;
    var xhr = xmlhttp();
    if (!xhr)
        return;
    var type = (opts.type||'get').toUpperCase();
    if (!(type in REQUESTS))
        throw new Error('Wrong request type');
    var data = REQUESTS[type](url, qry, opts);
    if (processor.prepare)
        processor.prepare();
    xhr.open(type, this.url_prefix+url+data.uri, true);
    xhr.onreadystatechange = processor.done(xhr, opts.done);
    if (data.headers){
        var hdr = Object.keys(data.headers);
        for (var h=0; h<hdr.length; ++h)
            xhr.setRequestHeader(hdr[h], headers[hdr[h]]);
    }
    xhr.send(data.request);
};
Ajax.load = A.load.bind(new Ajax());

return Ajax;
});
