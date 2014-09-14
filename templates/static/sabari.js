requirejs.config({});
requirejs([], function(){
    /*tagger = element.create('div', {'id': 'tagger'});    
    element.appendChild(document.body, [
                        tagger, [
                            element.create('div', {'id': 'tagbox'}),
                            element.create('img', {'src': '/icon/add.png'})
                            ]
                        ]);
    var imgs = document.getElementsByTagName('img');    
    for(var i = 0; i < imgs.length; i++){
        var img = imgs[i];
        if(!img.name || img.tagName != 'IMG') continue;
        img.onmouseover = function(){ showTagManager(this);};
    }*/
/*    function showTagManager(image){
        if(!image || !image.parentNode) return;
        var tagger = document.getElementById('tagger');
        var tagbox = document.getElementById('tagbox');    
        if(!tagger || !tagbox) return;
        tagger.style.display = 'block';
        element.appendChild(tagger.parentNode, [tagbox.childNodes[0]]);
        element.appendChild(image.parentNode, [tagger]);
        element.appendChild(tagbox, [image]);
    }*/

    function set_columns(){
        var columns = Math.floor(window.innerWidth / 200);
        if (columns == 4)
            return;
        var elems = document.querySelectorAll('.entity');
        var rows = document.querySelectorAll('.row');
        var tbody = document.querySelector('.holder');
        var data = [];
        var row = null;
        for (var i=0; i<elems.length; ++i){
            if (!(i % columns))
                data.push.apply(data, [{tr: {className: 'row'}}, row = []]);
            row.push(elems[i]);
        }
        element.appendChild(tbody, data);
        element.remove(Array.prototype.slice.call(rows));
    }

    function add_event(obj, evType, fn){
        if (!obj)
            return false;
        if (obj.addEventListener){
            obj.addEventListener(evType, fn, false);
            return true;
        } else if(obj.attachEvent)
            return obj.attachEvent("on" + evType, fn);
        else
            return false;
    }

    add_event(window, 'load', set_columns);
    if (document.readyState === "complete")
        set_columns();
});


