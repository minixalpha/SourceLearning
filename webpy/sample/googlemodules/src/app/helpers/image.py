# Author: Alex Ksikes 

# TODO:
# - should be made into a class

import Image, cStringIO, os

def save(fi, filename, min_width=30, min_height=20, max_width=460, max_height=420, max_kb=40):
    im = get_image_object(fi)
    width, height = im.size
    
    if min_width <= width <= max_width and min_height <= height <= max_height:
        if len(fi) <= max_kb * 1024:
            open(filename, 'wb').write(fi)
        else:
            compress(im, filename)
    else:
        thumbnail(im, filename, max_width, max_height)
        if os.path.getsize(filename) > max_kb * 1024:
            compress(im, filename)

def get_image_object(fi):
    if not isinstance(fi, file):
        fi = cStringIO.StringIO(fi)
    
    im = Image.open(fi)
    if im.mode != "RGB": 
        im = im.convert("RGB")
        
    return im
    
def compress(im, out):
    im.save(out, format='jpeg')

def thumbnail(im, out, max_width, max_height):
    im.thumbnail((max_width, max_height), Image.ANTIALIAS)
    im.save(out)