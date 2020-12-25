from pathlib import Path

import xml.etree.ElementTree
import collections

def osm(file):
    items=list()
    with open(file) as f:
        for event, elem in xml.etree.ElementTree.iterparse(f):
            tags=dict()
            if elem.tag=="node":
                tags["lat"]=elem.get("lat")
                tags["lon"]=elem.get("lon")
                tags["osmtype"]="node"
            elif elem.tag=="way":
                tags["osmtype"]="way"
            elif elem.tag=="relation":
                tags["osmtype"]="relation"
            else:
                continue
            tags["osmid"]=elem.get("id")
            for child in elem:
                if child.tag=="tag":
                    tags[child.get("k")]=child.get("v")
                if child.tag=="center":
                    tags["lat"]=child.get("lat")
                    tags["lon"]=child.get("lon")
            if "contact:website" in tags and "website" not in tags:
                tags["website"]=tags["contact:website"]
            tags['inputfile']=file
            items.append(tags)
    return items

#~ data=osm('merged.xml')
print('Loading data…')
data=list()
#~ for state in ['Michigan.osm','Ohio.osm','Wisconsin.osm']:
for state in sorted(Path('.').glob('*.osm')):
	data=data+osm(state)

worduse=collections.defaultdict(collections.Counter)
seen=collections.Counter()
printcount=0
nonecount=0
print('Calculating frequencies…')
for item in data:
	rel,name=item['religion'],item.get('name',None)
	if name is None:
		nonecount+=1
	else:
		for word in name.lower().split():
			worduse[word][rel]+=1
			seen[word]+=1
# common words
skips={"-", "&", "and", "at", "for", "in", "of", "on", "the", "new", "inc",
           "academy", "preschool", "school", "cemetery", "education",
          "cultural","community","center","society"}
# Words that (subjectively) don't have much signal for a particular religion
ownwords={
    'ascended_master_teachings':{'sanctuary'},
    'buddhist':{'temple'},
    'christian':{'circle','church','emanuel','sinai','souls','temple','congregation'},
    'hindu':{'temple'},
    'jewish':{'beth','congregation','hebrew','israel','sinai','shalom','temple','zion'},
    'multifaith':{'chapel'},
    'muslim':set(),
    'scientologist':{'church'},
    'sikh':{'temple'},
    'unitarian_universalist':{'church','congregation','unitarian','universalist'}
    }
matches=list()
for item in data:
	msg=""
	score=0
	rel,name=item['religion'],item.get('name',None)
	itemskips=skips | ownwords.get(rel,set())
	if name is None:
		pass
	elif rel in {'all','none'}:
		pass
	else:
		for word in name.lower().split():
			if word.lower() not in itemskips:
				for relg,count in worduse[word].items():
					if count > 0 and seen[word] > 10 and relg !=rel:
						rat=count/seen[word]
						if rat > 0.099:
							score+=rat
							msg=msg+"{} {} {} {:.2f}\n".format(relg, word, count, rat)
	if msg:
		matches.append((score,item,msg))
matches.sort(key=lambda z: -1*z[0])
for row in matches:
	score, item, msg=row
	rel,name=item['religion'],item.get('name',None)
	print("{:.2f}".format(score), name, rel, item['inputfile'], "http://openstreetmap.org/"+item["osmtype"]+"/"+item["osmid"])
	print(msg, end="--\n")
		
print(len(matches), nonecount, len(data))

