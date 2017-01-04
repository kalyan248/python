import os
import sys
import time

start = time.time()
mydir= sys.argv[1]
skey = sys.argv[2].lower()
found= "N"

i=0

print("Searching for .... '"+ sys.argv[2] +"'")
for root,subdirs,files in os.walk(mydir):	
	for f in files:		
		if f.lower().find(skey,0,len(f))>0:
			found = "Y"
			print(root+'\\'+f)			
			i+=1
done = time.time()
if found =="N":
	print('Could not find: '+str(sys.argv[2]))
else:
	print(str(i) + ' file(s) found.')