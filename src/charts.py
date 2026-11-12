import json, pathlib
def N(k,c,r,e=None,n=None,span=1,t=None,s=None,future=False,color=None):
    d=dict(k=k,c=c,r=r,n=n,span=span)
    if e is not None: d['e']=e
    if t: d['t']=t
    if s: d['s']=s
    if future: d['future']=True
    if color: d['color']=color
    return d
def L(a,b,l=None,future=False,color=None):
    d=dict(a=a,b=b)
    if l: d['l']=l
    if future: d['future']=True
    if color: d['color']=color
    return d
C=lambda name,color,sub=None: dict(name=name,color=color,sub=sub)
RED,GOLD,VIO,TEAL,ORA,SKY,GRAY='#EF5350','#F4B740','#9B7BFF','#2EC4B6','#FF8A3D','#5AB0FF','#8C88C0'

phases=[
 dict(n=1,years='2008 to 2012',peak='The Avengers',sum="Iron Man, the Hulk, Thor and Captain America are introduced one at a time, then Nick Fury brings them together to stop Loki's alien invasion of New York. Thanos is revealed as the power behind it."),
 dict(n=2,years='2013 to 2015',peak='Avengers: Age of Ultron',sum="Infinity Stones keep surfacing. S.H.I.E.L.D. falls to HYDRA, the Guardians of the Galaxy form, and Tony's Ultron program nearly wipes out humanity. Thanos decides to collect the Stones himself."),
 dict(n=3,years='2016 to 2019',peak='Avengers: Endgame',sum="The Avengers split over government control and Thanos wipes out half of all life. Five years later the survivors travel through time to undo it, at the cost of Tony Stark and Natasha Romanoff."),
 dict(n=4,years='2021 to 2022',peak='Doctor Strange in the Multiverse of Madness',sum="The world adjusts to everyone's return, new heroes take up old names, Loki breaks the single timeline into a multiverse, and Doctor Strange's spells pull in other universes."),
 dict(n=5,years='2023 to 2025',peak='Thunderbolts*',sum="Kang the Conqueror appears, the Fox mutant universe joins the multiverse, Sam Wilson becomes Captain America, and a team of misfits becomes the New Avengers as other worlds start arriving."),
 dict(n=6,years='2025 to 2027',peak='Avengers: Doomsday and Secret Wars',sum="The Fantastic Four cross over from their own universe, Spider-Man meets the mutant Jean Grey, Vision reunites with his sons, and Doctor Doom faces heroes from three universes in Avengers: Doomsday."),
]

stones=dict(key='stones',chip='The Infinity Stones',title='The six Infinity Stones',type='flow',noHead=True,
 intro="Where each Stone first appears and how Thanos gets it. Tap a Stone to open the film it first appears in.",
 cols=[C('Space',SKY),C('Mind',GOLD),C('Reality',RED),C('Power',VIO),C('Time',TEAL),C('Soul',ORA)],
 nodes=[N('sp',0,0,4,t='Space Stone',s='Inside the Tesseract',n="Thanos crushes the Tesseract on the Asgardian refugee ship. Loki had stolen it."),
        N('mi',1,0,5,t='Mind Stone',s="Loki's scepter, then Vision",n="Thanos rips it out of Vision's forehead in Wakanda."),
        N('re',2,0,7,t='Reality Stone',s='The Aether',n="Taken from the Collector on Knowhere."),
        N('po',3,0,9,t='Power Stone',s='The Orb',n="Taken by destroying the planet Xandar, off-screen."),
        N('ti',4,0,13,t='Time Stone',s='The Eye of Agamotto',n="Doctor Strange hands it over to save Tony's life on Titan."),
        N('so',5,0,18,t='Soul Stone',s='Hidden on Vormir',n="Thanos sacrifices Gamora, the person he loves."),
        N('ga',0,1,None,span=6,t='The Infinity Gauntlet',s='All six together',n="Thanos gathers every Stone in Avengers: Infinity War.",color=VIO),
        N('sn',0,2,18,span=6,t='The Snap',s='Avengers: Infinity War',n="Half of all life in the universe turns to dust.",color=VIO),
        N('he',0,3,21,span=6,t='The Time Heist',s='Avengers: Endgame',n="The Avengers borrow every Stone from the past, Hulk snaps everyone back, and Tony snaps Thanos away.",color=VIO)],
 links=[L(x,'ga') for x in ['sp','mi','re','po','ti','so']]+[L('ga','sn'),L('sn','he','Five years later')])

story_ids=[4,20,0,2,1,3,5,7,6,8,9,14,10,11,12,23,17,15,13,16,19,18,21,22,24,25,26,27,33,28,29,30,31,32,34,35,37,38,39,36]
story_labels=['1940s','1995','2008','2010','2010','2010','2012','2013','2013','2014','2014','2014','2015','2015','2016','2016','2016','2016','2016','2017','2018','2018','2018 to 2023','2024','2024','2024','2024','2024','2024','2025','2025','2026','2026','2026','About 2027','About 2027','About 2028','About 2028','Unknown','1964, another universe']
storyc=dict(key='story',chip='The story in in-universe order',title='The story in in-universe order',type='story',
 intro="Release order is best for a first watch. This is the order events happen inside the story, based on Marvel's own timeline. Years after 2023 are approximate.")

spider=dict(key='spider',chip='How the Spider-Man films connect',title='How the Spider-Man films connect',type='flow',
 intro="Three Spider-Men in three universes, plus Venom's world, all collide in Spider-Man: No Way Home.",
 cols=[C('Tobey Maguire',RED,'Earth-96283'),C('Andrew Garfield',SKY,'Earth-120703'),C('Tom Holland',GOLD,'Main universe'),C("Venom's world",TEAL,'Earth-688')],
 nodes=[N('s1',0,0,40,n="The Green Goblin dies."),N('s2',0,1,41,n="Doctor Octopus dies."),N('s3',0,2,42,n="Sandman, and Venom is destroyed."),
        N('a1',1,2,43,n="The Lizard; Captain Stacy dies."),N('a2',1,3,44,n="Electro; Gwen Stacy dies."),
        N('h1',2,3,45,n="Tony Stark recruits Peter."),N('h2',2,4,46,n="Peter stops the Vulture."),N('v1',3,4,54,n="Eddie Brock bonds with Venom."),
        N('h3',2,5,47,n="Peter turns to dust, then returns."),N('h4',2,6,48,n="Mysterio reveals who Peter is."),N('v2',3,6,55,n="Credits: pulled into the main universe."),
        N('h5',2,7,49,n="All three Peters meet. The world forgets Peter Parker."),
        N('v3',3,8,56,n="The Vulture lands in this world."),N('h6',2,8,50,n="Peter meets the mutant Jean Grey."),N('v4',3,9,58,n="Venom dies; Knull waits."),
        N('d',2,9,38,n="Spider-Man's role not announced.")],
 links=[L('s1','s2'),L('s2','s3'),L('a1','a2'),L('h1','h2'),L('h2','h3'),L('h3','h4'),L('h4','h5'),L('v1','v2'),
        L('s3','h5','Villains and Tobey'),L('a2','h5','Villains and Andrew'),L('v2','h5','Eddie pulled in'),
        L('h5','v3','Vulture thrown out, Eddie sent home',color=TEAL),L('v3','v4'),L('h5','h6'),L('h6','d',future=True)])

sony=dict(key='sony',chip="How Sony's universe connects",title="How Venom's world touches the main universe",type='flow',
 intro="Only two crossings matter: Eddie Brock's trip through Spider-Man: No Way Home, and the Vulture being thrown into Morbius's world.",
 cols=[C("Venom's world",TEAL,'Earth-688'),C('Main universe',GOLD,'Earth-616')],
 nodes=[N('v1',0,0,54,n="Credits tease Carnage."),N('v2',0,1,55,n="Credits: Eddie is pulled across."),N('nwh',1,2,26,n="Eddie learns about the Avengers, then is sent home."),
        N('mo',0,3,56,n="The Vulture appears in a prison cell."),N('mw',0,4,57,n="Standalone, set in 2003."),N('ld',0,5,58,n="Venom dies saving Eddie."),N('kr',0,6,59,n="Standalone."),
        N('end',0,7,None,t='Series paused',s='August 2026',n="Sony says no films are in active development.",color=GRAY)],
 links=[L('v1','v2'),L('v2','nwh','Eddie pulled in'),L('nwh','mo','Vulture thrown out',color=TEAL),L('nwh','ld','Eddie sent home',color=TEAL),
        L('mo','mw'),L('mw','ld'),L('ld','kr'),L('kr','end',future=True)])

wanda=dict(key='wanda',chip='The Wanda, Vision and Agatha trilogy',title="The story of Wanda, Vision and their sons",type='flow',
 intro="Five films set up Wanda and Vision, then three shows (an official trilogy) follow Wanda, Agatha with Wanda's son Billy, and Vision. All three threads now lead to Avengers: Doomsday.",
 cols=[C('Wanda',RED),C('Agatha and Billy',VIO),C('Vision',GOLD)],
 nodes=[N('ws',0,0,8,n="Credits: Wanda and Pietro first seen."),N('ao',0,1,10,span=3,n="Pietro dies. Vision is born from the Mind Stone."),
        N('cw',0,2,12,span=3,n="Wanda and Vision fall for each other."),N('iw',0,3,18,span=3,n="Thanos takes the Mind Stone and Vision dies."),
        N('eg',0,4,21,n="Wanda returns and nearly beats Thanos alone."),
        N('wv',0,5,60,span=3,n="Grief builds a fake town, a Vision and two sons. Wanda becomes the Scarlet Witch."),
        N('mm',0,6,27,n="Wanda hunts other universes for her sons, then destroys the Darkhold."),
        N('ag',1,6,72,n="Billy is reborn. Agatha returns as a ghost to help find Tommy."),
        N('vq',2,7,79,n="Vision beats the man behind Ultron's face and reunites with Tommy and Billy. Credits: Doctor Doom wakes Wanda."),
        N('dm',0,8,38,span=3,n="Wanda returns, in Doctor Doom's hands.")],
 links=[L('ws','ao'),L('ao','cw'),L('cw','iw'),L('iw','eg',color=RED),L('eg','wv',color=RED),
        L('wv','mm','The Darkhold',color=RED),L('wv','ag','Agatha trapped as Agnes',color=VIO),L('wv','vq','White Vision flies off',color=GOLD),
        L('ag','vq','Searching for Tommy',color=VIO),L('mm','dm','Doom wakes Wanda',future=True,color=RED),L('vq','dm',future=True)])

street=dict(key='street',chip='The street-level shows',title='From Netflix to Disney+: Daredevil and the street-level heroes',type='flow',
 intro="The Netflix shows became official in 2024. The same actors carry their characters into the main universe.",
 cols=[C('Netflix shows',GOLD,'2015 to 2019'),C('Main universe',RED,'2021 onward')],
 nodes=[N('dd',0,0,80,n="Kingpin, the Punisher, Elektra and the Hand."),N('jj',0,1,81),N('lc',0,2,82),N('if',0,3,83),
        N('df',0,4,84,n="The four team up against the Hand."),N('pn',0,5,85,n="Frank finishes his war of revenge."),
        N('nwh',1,1,26,n="Matt Murdock, lawyer, returns."),N('hk',1,2,63,n="The Kingpin returns."),N('sh',1,3,66,n="Daredevil returns."),
        N('ec',1,4,71,n="Maya faces the Kingpin."),N('b1',1,6,73,n="Foggy is killed. Fisk becomes mayor."),
        N('b2',1,7,77,n="Jessica Jones returns. Matt reveals he is Daredevil."),N('ol',1,8,78,n="Frank finds a reason to go on."),
        N('bn',1,9,37,n="The Punisher and the Hand meet Spider-Man."),
        N('b3',1,10,None,t='Daredevil: Born Again, Season 3',s='March 2027',future=True)],
 links=[L('dd','jj'),L('jj','lc'),L('lc','if'),L('if','df'),L('df','pn'),
        L('dd','nwh','Same Matt Murdock'),L('nwh','hk'),L('hk','sh'),L('sh','ec'),L('ec','b1'),L('b1','b2'),L('b2','ol'),L('ol','bn'),L('bn','b3',future=True),
        L('pn','b1','The Punisher returns')])

loki=dict(key='loki',chip='Loki and the multiverse',title='How the multiverse opened up',type='flow',
 intro="The Loki show is where the Multiverse Saga really begins. Kang was set up as the big villain, then dropped in 2023; Doctor Doom took his place.",
 cols=[C('Shows and events',TEAL),C('Films',VIO)],
 nodes=[N('eg',1,0,21,n="The 2012 Loki escapes with the Tesseract."),
        N('l1',0,1,62,n="He Who Remains dies. One timeline becomes a multiverse."),
        N('nw',1,2,26,n="Strange's spell pulls in other universes."),N('mm',1,3,27,n="Incursions: universes collide."),
        N('qm',1,4,30,n="Kang the Conqueror and the Council of Kangs."),
        N('l2',0,5,70,n="Loki holds the multiverse together as the God of Stories."),
        N('ka',0,6,None,t='Kang dropped',s='December 2023',n="Marvel parts ways with actor Jonathan Majors.",color=GRAY),
        N('ma',1,6,32,n="Monica is trapped in an X-Men universe."),N('dw',1,7,33,n="The Fox universe joins the multiverse."),
        N('bw',1,8,34,n="Credits: other worlds are coming."),N('tb',1,9,35,n="Credits: a ship from another universe arrives."),
        N('fs',1,10,36,n="Credits: Doctor Doom appears."),N('dm',1,11,38,n="Doctor Doom against three universes."),N('sw',1,12,39)],
 links=[L('eg','l1','Loki arrested by the Time Variance Authority'),L('l1','nw'),L('nw','mm'),L('mm','qm'),L('qm','l2'),L('l2','ma'),L('qm','ka',future=True,color=GRAY),
        L('ma','dw'),L('dw','bw'),L('bw','tb'),L('tb','fs'),L('fs','dm'),L('dm','sw',future=True),L('ka','dm','Replaced by Doctor Doom',future=True,color=GRAY)])

xmen=dict(key='xmen',chip='How the X-Men films connect',title='Two timelines and a door into the main universe',type='flow',
 intro="Days of Future Past rewrites 1973, so the later Fox films follow a new history. Deadpool & Wolverine saves that universe and links it to the main one.",
 cols=[C('Original timeline',GOLD),C('Revised timeline',SKY),C('Main universe',ORA)],
 nodes=[N('fc',0,0,96,span=2,n="How the X-Men began, in 1962."),N('or',0,1,95,n="Logan gets his adamantium skeleton."),N('xm',0,2,92),
        N('x2',0,3,93,n="Jean dies at Alkali Lake."),N('ls',0,4,94,n="The Phoenix kills Cyclops and Xavier."),N('wo',0,5,97,n="Credits: Xavier and Magneto return."),
        N('df',0,6,98,span=2,n="Wolverine rewrites 1973. A new, peaceful future."),
        N('ap',1,7,100),N('dp',1,8,103,n="Jean takes the Phoenix force and seems to die."),N('d1',1,9,99),N('d2',1,10,102),N('nm',1,11,104),N('lo',1,12,101,n="Logan dies in 2029."),
        N('mz',2,7,65,n="Kamala has a mutation."),N('mo',2,8,27,n="Professor X of another universe."),N('wf',2,9,29,n="Namor calls himself a mutant."),N('mr',2,10,32,n="Credits: Beast."),
        N('dw',1,13,105,span=2,n="Deadpool's universe is saved and joins the multiverse."),
        N('bn',2,14,37,n="Jean Grey arrives in the main universe."),
        N('dm',0,15,38,span=3,n="The original X-Men join the Avengers against Doctor Doom.")],
 links=[L('fc','or',color=GOLD),L('or','xm'),L('xm','x2'),L('x2','ls'),L('ls','wo'),L('wo','df'),L('df','ap','History rewritten',color=SKY),L('ap','dp'),L('dp','d1'),L('d1','d2'),L('d2','nm'),L('nm','lo'),
        L('lo','dw','Logan is the anchor'),L('mz','mo'),L('mo','wf'),L('wf','mr'),L('mr','dw',color=ORA),L('dw','bn',color=ORA),L('bn','dm',future=True),L('dw','dm',future=True,color=SKY)])

ff=dict(key='ff',chip='How the Fantastic Four films connect',title='Five Fantastic Fours, one crossing',type='flow',
 intro="The early films are separate. The Marvel Studios family lives in its own universe until their ship crosses into the main one.",
 cols=[C('Earlier versions',GRAY,'Each one separate'),C('Marvel Studios',SKY,'Including cameos')],
 nodes=[N('f94',0,0,107,n="Made to keep the film rights; never released."),N('f05',0,1,108,n="Chris Evans plays Johnny Storm."),
        N('f07',0,2,109,n="Galactus and the Silver Surfer."),N('f15',0,3,110,n="A standalone reboot."),
        N('mm',1,1,27,n="An alternate Reed Richards."),N('dw',1,2,33,n="Fox's Johnny Storm returns in the Void."),
        N('fs',1,3,111,n="Franklin is born. Credits: Doctor Doom."),N('tb',1,4,35,n="Credits: their ship enters the main universe."),
        N('dm',1,5,38),N('sw',1,6,39)],
 links=[L('f05','f07'),L('f05','dw','Chris Evans returns'),L('mm','dw'),L('dw','fs'),L('fs','tb'),L('tb','dm'),L('dm','sw',future=True)])

routes=[
 dict(key='doomsday',name='Ready for Doomsday',color=SKY,ids=[92,93,98,18,21,60,62,27,29,70,33,34,35,36,79,38],
      intro="The shortest path to Avengers: Doomsday: the Fox X-Men who return, the end of the last saga, and everything that sets up Doctor Doom and Wanda. A suggested shortlist, not an official one."),
 dict(key='starter',name='Infinity Saga in nine films',color=GOLD,ids=[0,5,8,9,12,16,17,18,21],
      intro="Short on time? These nine films carry the Thanos story from start to finish. A suggested shortlist; you will miss some introductions, and the stories fill the gaps."),
 dict(key='infinity',name='The full Infinity Saga',color=VIO,ids=list(range(23)),
      intro="All twenty-three films from Iron Man to Spider-Man: Far From Home. One complete story with a real ending."),
 dict(key='wanda',name='Wanda and Vision',color=RED,ids=[10,12,18,21,60,27,72,79,38],
      intro="Their whole story in nine stops, ending where the last VisionQuest credits scene points: Avengers: Doomsday."),
]
soon=[
 dict(date='2026-12-18',title='Avengers: Doomsday',kind='Film',e=38,note="Doctor Doom against the Avengers, the Fantastic Four and the X-Men. Tickets are on sale."),
 dict(date='2027-03-01',month=True,title='Daredevil: Born Again, Season 3',kind='Show',note="Reported to be the final season."),
 dict(date='2027-06-18',title='Spider-Man: Beyond the Spider-Verse',kind='Film',e=53,note="The end of Miles Morales's animated trilogy, from Sony."),
 dict(date='2027-12-17',title='Avengers: Secret Wars',kind='Film',e=39,note="The end of the Multiverse Saga."),
 dict(date='2028-05-05',title='X-Men',kind='Film',note="Marvel Studios' first X-Men film, with a new cast for the main universe. Jake Schreier directs."),
 dict(date='2028-07-28',title='Ghost Rider',kind='Film',note="Ryan Gosling plays Johnny Blaze. Shawn Levy directs."),
 dict(date='2028-12-15',title='Black Panther 3',kind='Film',note="Ryan Coogler returns to direct."),
]
# Order used by share codes. FROZEN: only ever append new ids at the end, or old links will decode wrongly.
share_order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 40, 41, 42, 43, 44, 51, 52, 53, 54, 55, 56, 57, 58, 59, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 96, 95, 92, 93, 94, 97, 98, 100, 103, 99, 102, 104, 101, 106, 107, 108, 109, 110]
# "How they were received": ranked by IMDb or the Tomatometer, from src/ratings.json (see scripts/ratings.py)
ratings_main=dict(key='ratings-main',chip='How the films were received',title='How every film was received',type='ratings',scope='main',
  intro="Every Marvel Studios film ranked by its IMDb rating or its Rotten Tomatoes Tomatometer. Switch between them to see where audiences and critics disagree.")
ratings_shows=dict(key='ratings-shows',chip='How the shows were received',title='How every show was received',type='ratings',scope='shows',
  intro="The shows ranked the same way. A single season gets the average IMDb rating of its episodes.")
data=dict(phases=phases,routes=routes,soon=soon,share=share_order,story=dict(ids=story_ids,labels=story_labels),sections=dict(
  main=[dict(key='phases',chip='The Phases at a glance',title='The six Phases at a glance',type='ribbon',intro="Width shows how many films each Phase has. Tap a Phase to jump to it on the main line."),stones,storyc,ratings_main],
  spider=[spider],sony=[sony],shows=[wanda,street,loki,ratings_shows],xmen=[xmen],ff=[ff]))
assert len(story_ids)==len(story_labels)==40 and sorted(story_ids)==list(range(40))
out=pathlib.Path(__file__).resolve().parent/'charts.json'
text=json.dumps(data,ensure_ascii=False)
if '--check' in __import__('sys').argv:
    if not out.exists() or out.read_text()!=text: raise SystemExit('Out of date, run python3 src/charts.py: src/charts.json')
    print('Up to date')
else:
    out.write_text(text)
    print('ok')
