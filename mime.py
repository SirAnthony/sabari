
import mimetypes
extensions_map = mimetypes.types_map.copy()
extensions_map.update({
    '': 'text/html', # Default
})

def guessType(path):
    """return a mimetype for the given path based on file extension."""
    base, s, ext = path.rpartition('.')
    ext = s + ext #FUFU
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']
