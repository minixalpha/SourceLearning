import web
db = web.database(dbn='mysql', db='googlemodules', user='ale', passwd='3babes')

for url in db.select('modules', what='screenshot'):
    print 'http://www.googlemodules.com/image/screenshot/' + url.screenshot
