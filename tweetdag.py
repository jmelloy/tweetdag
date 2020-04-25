from urllib2 import urlopen, URLError
from user import User
import sys
import json
import psycopg2
import cPickle
import time
from copy import copy

conn = psycopg2.connect("dbname='jmelloy'")
cursor = conn.cursor()

screenname = sys.argv[1]

central_user = User(screenname, conn, True)
central_user.save()

users = set(central_user.followers(True))

user_follow = {}
users.add(central_user.id)

blacklist = ["BarackObama", "MrTweet", "tweet140", "yourheart", "yourpenis", "plusplusbot"]
#blacklist = []

user_hash = {central_user.id:central_user}

sql = "insert into twitter_followers values (%(id)s, %(data)s)"
failed = []
for u in users:
    print u
    usr = User(u, conn)
    usr.save()
    
    if usr.hitTwitter:
        time.sleep(40)
    user_hash[u] = usr

    follow = usr.followers()
    if usr.hitTwitter:
        time.sleep(40)

    if follow != None:
        follows = [a for a in follow if a in users]
        user_follow[u] = follows
        usr.follows = len(follows) + 1
    else:
        print "Failwhale!"
        time.sleep(30)
        failed.append(u)

user_follow[central_user.id] = []

print "%d Failed: " % len(failed), failed
filename = "%s.obj" % central_user.screen_name
print "Writing file %s" % filename

file = open(filename, "w")

cPickle.dump(user_follow, file, 2)

file.close()

for u in user_follow.keys():
    for f in user_follow[u]:
        user_hash[f].following += 1


order = []
for u in user_hash:
    if user_hash[u].follows == 0:
        order.append((0, user_hash[u]))
    else:
        #order.append(((float(user_hash[u].following) / user_hash[u].follows), user_hash[u]))
        order.append((user_hash[u].follows, user_hash[u]))

order.sort()
order.reverse()

for o in order:
    usr = o[1]
    print usr.screen_name, "Follows:", usr.follows, "Following:", usr.following, "/", float(usr.following) / usr.follows

remove = set([])
for u in user_hash:
    if float(user_hash[u].following) / user_hash[u].follows >= 2.0 and user_hash[u].follows < 5 and user_hash[u].following > 5:
        remove.add(u)

    if user_hash[u].screen_name in blacklist:
        remove.add(u)
    
    if user_hash[u].following < 2 or user_hash[u].follows < 2:
        remove.add(u)
    
for r in remove:
    print 'Removing %s' % user_hash[r].screen_name
    del user_hash[r]


print "Writing dot file ... "
graph = open("%s.dot" % central_user.screen_name, "w")

graph.write("digraph social {\n")
#graph.write("node [shape = none, style=rounded];\n")
#graph.write("edge [len=3.0];\n")
#graph.write("graph [overlap='scale', separation='.5'];\n")
graph.write('graph [label="%s", overlap=false, sep="0.25", splines=true];\n' % central_user.screen_name)
graph.write('node [shape=rectangle, penwidth=0.0];\n')
for o in order:
    
    u = o[1].id
    if u in user_hash:
        usr = user_hash[u]
        graph.write('"%s" [image="%s", label="", tooltip="%s", URL="http://twitter.com/%s"];\n' % (usr.screen_name,  usr.filename, usr.screen_name, usr.screen_name))
        for follows in user_follow[u]:
            if follows in user_hash:
                graph.write('"%s" -> "%s";\n' % (usr.screen_name,
                    user_hash[follows].screen_name))

graph.write("};")

graph.close()
conn.commit()
conn.close()
