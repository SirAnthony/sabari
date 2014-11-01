require.config({});

define(['lib/element', 'ajax.min'], function(L, Ajax){

function $(selector){
    var item = document.querySelector(selector);
    if (item)
        item.append = L.appendChild.bind(L, item);
    return item;
}
function $$(selector){
    return document.querySelectorAll(selector); }

function entity(data){
    var img = {src: data.src||'', alt: data.alt||'',
        name: data.name||''};
    if (data.w)
        img.width = data.w;
    var out = [{a: {href: data.href}}, [{img: img}, 'br']];
    if (data.desc)
        out[1].push({'': {textContent: data.desc}});
    return L.create('td', {className: 'entity'}, out);
}

var processor = new Ajax.processor({
    data: function(data){
        var d = data.data;
        var columns = Math.floor(window.innerWidth / 200);
        columns = Math.floor((window.innerWidth-columns*2-10)/200);
        var holder = $('.holder');
        var row = holder.lastChild;
        var elems = d.items;
        var count = columns - row.children.length;
        for (var offset=0; offset<count; ++offset)
            L.appendChild(row, entity(elems[offset]));
        var images = [];
        for (var i=0; i<elems.length-count; ++i){
            if (i%columns === 0){
                holder.append([{tr: {className: 'row'}}, images]);
                images = [];
            }
            images.push(entity(elems[count+i]));
        }
        holder.append([{tr: {className: 'row'}}, images]);
        $('input#page').value = d.page >= d.pages-1 ? -1 : d.page;
    }
});
processor.catch$ = function(err){ throw err; };

var doc_body = document.documentElement || document.body.parentNode || document.body;
function scroll(){
    var scrollTop = window.pageYOffset||doc_body.scrollTop;
    if (doc_body.offsetHeight - scrollTop - window.innerHeight < 300){
        if (processor.lock)
            return;
        var current = parseInt($('input#page').value);
        if (current<0)
            return;
        processor.lock = true;
        Ajax.load('./', {p: current+1, json: 1},
                {processor: processor});
        processor.processed = function(){
            this.lock = false;
            this.processed = function(){};
        };
    }
}

function resize(){
    var columns = Math.floor(window.innerWidth / 200);
    columns = Math.floor((window.innerWidth-columns*2-10)/200);
    // Skip if same
    if (columns == $('.row').children.length)
        return;
    var elems = $$('.entity');
    var old_rows = $$('.row');
    var data = [];
    for (var i=0; i<elems.length; i+=columns){
        data.push({tr: {className: 'row'}});
        data.push(Array.prototype.slice.call(elems, i, i+columns));
    }
    $('.holder').append(data);
    L.remove(old_rows);
}

function add_event(obj, evType, fn){
    if (!obj)
        return false;
    if (obj.addEventListener){
        obj.addEventListener(evType, fn, false);
        return true;
    } else if(obj.attachEvent)
        return obj.attachEvent('on'+evType, fn);
    else
        return false;
}

function onload(func){
    if (document.readyState=='complete')
        return func();
    add_event(window, 'load', func);
}

onload(resize);
add_event(window, 'resize', resize);
if ($('input#page'))
    add_event(window, 'scroll', scroll);
});


