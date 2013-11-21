# Author: Alex Ksikes 

import random, re, sets

stop_words = ['for', 'and', 'any', 'or', 'in', 'of', 'to']

def make_cloud(tags, min_tag_length=0, min_count=0, max_count=0, 
    plurial=True, normalize=False, randomize=False, alpha=True):
    """Assumes tags come as an iterator [dict(tag=tag_name, count=count_value), ...."""
    counts = {}
    for t in tags:
        tag, count = get_clean_tag(t.tag), t.count
        
        # no stop word, must have min size
        if tag in stop_words or (min_tag_length and len(tag) < min_tag_length):
            continue
            
        # min count but give a chance to small counts if in randomized
        if count < min_count:
            if randomize and random.randint(0,100) < 15:
                pass
            else:
                continue
            
        # group singular and plurial form together
        if plurial:
            tag, count = get_tag_representative(tag, count, counts)
        
        # cut off is at max_count
        if max_count and count >= max_count:
            count = max_count
            
        counts[tag] = count
        
    # normalizing between 0 and 1
    if normalize:
        max_count = max(counts.values())
        for tag, count in counts.items():
            counts[tag] = (1.0 * count - min_count) / (max_count - min_count)
    
    # the final result is sorted by tag name (alpha cloud)
    return sorted(counts.items())
#    return [dict(tag=tag, count=counts[tag]) for tag in sorted(counts.keys())]

def get_clean_tag(tag):
    return re.sub('\s{2,}', ' ', tag).strip()
    
def get_tag_representative(tag, count, counts):
    if tag[-1] == 's':
        tag_x = tag[:-1]
    else:
        tag_x = tag + 's'
    
    count_x = counts.get(tag_x, 0)
    if count_x > count:
        if counts.has_key(tag):
            del counts[tag]
        tag = tag_x
    elif count_x > 0:
        del counts[tag_x]
        
    count = max([count, count_x])
    
    return tag, count
