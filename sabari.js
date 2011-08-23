
window.onload = function(){
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
}

function showTagManager(image){
    if(!image || !image.parentNode) return;
    var tagger = document.getElementById('tagger');
    var tagbox = document.getElementById('tagbox');    
    if(!tagger || !tagbox) return;
    tagger.style.display = 'block';
    element.appendChild(tagger.parentNode, [tagbox.childNodes[0]]);
    element.appendChild(image.parentNode, [tagger]);
    element.appendChild(tagbox, [image]);
    
}

var element = new ( function(){
    
    this.downTree = function(funct, obj, er){
        for(var i=0; i < obj.childNodes.length; i++){
            var e = funct(obj.childNodes[i]);
            if(e) return e;
        }
        if(er) return 'ok';
    }
    
    this.addOption = function(obj, arr){
        if(arr.length){
            for(var i=0; i < arr.length; i++){            
                var opt = this.create('option', {value: arr[i], text: arr[i]});
                this.appendChild(obj, [opt]);
            }
        }else{
            for(var i in arr){
                var opt = this.create('option', {value: i, text: arr[i]});
                this.appendChild(obj, [opt]);
            }
        }
    }
    
    this.getChilds = function(obj){
        var childs = new Array();
        for(var i=0; i < obj.childNodes.length; i++){
            childs.push(obj.childNodes[i]);        
        }
        return childs;
    }
    
    this.removeAllChilds = function(el){
        while(el.hasChildNodes()){
            el.removeChild(el.lastChild);
        }
    }
    
    this.create = function(elem, params){
        if(!elem || elem == '') elem = 'text';
        var elm = document.createElement(elem);
        for (var i in params){ 
            elm[i] = params[i];
        }
        return elm;
    }
    
    this.appendChild = function(obj, arr){
        var ar = new Array();
        ar = eval(arr);
        var l = ar.length;
        if(!l) l = 0;
        for(var i=0; i < l; i++){
            if(!ar[i] || (!isElement(ar[i]) && !isArray(ar[i]) && !isHash(ar[i]))) continue;
            if(isHash(ar[i])){
                var el = ar[i];
                var type = el['elemType'];
                delete el['elemType'];
                ar[i] = this.create(type, el);
            }
            if(isArray(ar[i])){
                this.appendChild(ar[i-1], ar[i]);
            }else{
                obj.appendChild(ar[i]);
            }
        }
    }
})();

//################# Работа с куами.

var cookies = new ( function(){
    
    this.set = function(name, value, expires, path, domain, secure){
        document.cookie = name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");
    }
    
    this.del = function(name, path, domain){    
        document.cookie = name + "=" +
        ((path) ? "; path=" + path : "; path=/") +
        ((domain) ? "; domain=" + domain : "") +
        "; expires=Thu, 01-Jan-70 00:00:01 GMT;";
    }
    
    this.get= function(name){
        var cookie = " " + document.cookie;
        var search = " " + name + "=";
        var setStr = null;    
        if (cookie.length > 0) {
            var offset = 0;        
            offset = cookie.indexOf(search);    
            if (offset != -1) {
                offset += search.length;
                var end = 0;            
                end = cookie.indexOf(";", offset);             
                if (end == -1) end = cookie.length;            
                setStr = unescape(cookie.substring(offset, end));            
            }
        }
        return setStr;
    }
})();

//################# Классы

var pclass = new ( function(){

    this.hasClass = function(ele,cls){
        return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
    }

    this.add = function(ele,cls){
        if(!this.hasClass(ele,cls)) 
            ele.className += ' '+cls;
    }

    this.remove = function(ele,cls){
        if (this.hasClass(ele,cls)){
            var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
            ele.className=ele.className.replace(reg,'');
        }
    }
})();

function isElement(object){return !!(object && object.nodeType == 1);}
function isArray(object){return object != null && typeof object == "object" &&
    'splice' in object && 'join' in object;}
function isHash(object) {
    return object && 
        typeof object=="object" &&
        (object==window||object instanceof Object) &&
        !object.nodeName &&
        !isArray(object);
}
function isFunction(object){return typeof object == "function";}
function isString(object){return typeof object == "string";}
function isNumber(object){return typeof object == "number";}
function isUndef(object){return typeof object == "undefined";}