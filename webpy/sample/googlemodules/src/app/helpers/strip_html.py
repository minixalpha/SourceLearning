# Author: Alex Ksikes 

import HTMLParser

class HTMLStripper(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_fed_data(self):
        return ''.join(self.fed)

def strip(html):
    """Strip html and will also remove entities."""
    s = HTMLStripper()
    s.feed(html)
    return s.get_fed_data()