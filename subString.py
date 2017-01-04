#read fix log and split

import os

myList=[]
bStr= ""

with open("C:\\Kalyan_Office\\SametimeFileTransfers\\payloads.list",'r') as ff:
	lStr = ff.read().splitlines()
ff.close()

for l in lStr:	
	if(l.find('payload-')>=0) :		
		myList.append(l[:l.find(',')]+'.jar')
print(','.join(myList))