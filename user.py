from urllib2 import urlopen, URLError
from urllib import urlretrieve
import simplejson as json
import psycopg2
import os.path
from PIL import Image

class User:

    def __init__(self, userid, conn = None, forceHit = False):
        self.conn = conn
        
        self.follows = 1
        self.following = 1
        
        db = False

        if conn and not forceHit:
            cursor = conn.cursor()

            if type(userid) == int:
                sql = """select id, screen_name, image_filename, image_url
                    from twitter_ids
                    where id = %(id)s"""

                vars = {"id":userid}
            else:
                sql = """select id, screen_name, image_filename, image_url
                    from twitter_ids
                    where screen_name = %(id)s"""

                vars = {"id":userid}
                
            cursor.execute(sql, vars)

            rs = cursor.fetchone()

            if rs:
                self.id = rs[0]
                self.screen_name = rs[1]
                self.filename = rs[2]
                self.image_url = rs[3]
                self.needsSaving = False
                self.hitTwitter = False
                
                self.suffix = self.image_url.split('.')[-1]
                self.orig_filename = "images/%s.%s" % (self.screen_name, self.suffix)
                
                db = True

        if not db:
            print 'Hitting twitter for user'
            f = urlopen('http://twitter.com/users/show/%s.json' % userid)

            data = json.loads(f.read())

            f.close()

            self.id = data['id']
            self.screen_name = data['screen_name']
            self.image_url = data['profile_image_url']
            
            self.suffix = self.image_url.split('.')[-1]
            self.orig_filename = "images/%s.%s" % (self.screen_name, self.suffix)
            self.filename = "images/%s.png" % self.screen_name
            
            self.needsSaving = True
            self.hitTwitter = True
            
        if not os.path.exists(self.filename): 
            urlretrieve(self.image_url, self.orig_filename)
            
            im = Image.open(self.orig_filename)
            
            needsSaving = False

            if im.format <> "PNG":
                needsSaving = True

            if im.size != (48,48):
                print self.orig_filename, im.size
                im = im.resize((48,48), Image.ANTIALIAS)
                needsSaving = True

            if needsSaving:
                im.save(self.filename, "PNG")
            
            os.remove(self.orig_filename)
            

    def save(self):
        conn = self.conn
        if self.needsSaving and conn:
            cursor = conn.cursor()

            sql = """insert into twitter_ids (id, screen_name, image_url, image_filename)
                values (%(id)s, %(screen_name)s, %(image)s, %(image_file)s)"""

            vars = {
                "id":self.id,
                "screen_name":self.screen_name,
                "image":self.image_url,
                "image_file":self.filename
                }

            try:
                cursor.execute(sql, vars)
                conn.commit()
            except psycopg2.IntegrityError:
                conn.rollback()

    def followers(self, force=False):
        conn = self.conn
        cursor = conn.cursor()

        if not force:
            sql = """select follow_string
                from twitter_followers where id = %(id)s"""

            vars = {
                "id":self.id
            }

            cursor.execute(sql, vars)

            rs = cursor.fetchone()

            if rs:
                self.hitTwitter = False
                return json.loads(rs[0])

        try:
            print 'Hitting twitter for follower list'
            self.hitTwitter = True
            f= urlopen('http://www.twitter.com/friends/ids/%s.json' % self.id)

            data = f.read()

            try:
                self.follow = json.loads(data)
            except ValueError:
                print "No JSON data in stream."
                print data
                return None

            try:
                sql = """insert into twitter_followers
                    values (%(id)s, %(data)s)"""
                vars = {"id":self.id,"data":data}
                cursor.execute(sql, vars)
                conn.commit()
            except psycopg2.IntegrityError:
                conn.rollback()
                sql = """update twitter_followers
                    set follow_string = %(data)s
                    where id = %(id)s"""
                vars = {"id":self.id,"data":data}
                cursor.execute(sql, vars)
                conn.commit()

            return self.follow
        except URLError:
            return None

    def __str__(self):
        return self.screen_name
