#! parse xml

from xml.dom.minidom import parse
import xml.dom.minidom
import time,sys

assetTypesList = []
strategiesList = []
outputMsg = 'XML seems to be good, no invalid parameters found! Yayy!!';
regionName = ''
aName = ''
pList = []
pRefList = []
isError = False
typeDict = {}




def getAssetTypes(args):
	assetTypesList = args.getElementsByTagName("assetType")			
	return assetTypesList
#-----------------------------------------------------------

def getStrategies(args):
	strategiesList = args.getElementsByTagName('strategy')
	if not strategiesList:
		print('No "<strategy>" found for "'+ args.getAttribute('name')+'". Please verify XML!')
		if not assetTypesList:
			print('Exiting as no other Asset Types are there!')
			sys.exit();
	return strategiesList
#------------------------------------------------------------

def getParameters(args):
	parameters = args.getElementsByTagName("parameter")
	if not parameters:
		print('No "<parameter>" specified for strategy: "'+ args.getAttribute('name') +'"')
		print('proceeding to next strategy ...')
	return parameters
#-------------------------------------------------------------

def getLayouts(args):
	layouts = args.getElementsByTagName("lay:strategyLayout");	
	if not layouts:
		print('No "strategyLayout" specified for strategy: "'+ args.getAttribute('name') +'"')
		print('proceeding to next strategy ...')
	return layouts	
#-------------------------------------------------------------

def getParameterRefs(args):
	parameterRefs = args.getElementsByTagName("lay:control")
	return parameterRefs
#-------------------------------------------------------------

def noFurtherProcessing():
	print('\nExiting. No further processing!')
	sys.exit()
#-------------------------------------------------------------

def typeAttributesDict():
	typeStr = ''
	typeVar = []
	global typeDict

	typeStr = 'Int_t,Length_t,NumInGroup_t,SeqNum_t,TagNum_t,Float_t,Qty_t,Price_t,PriceOffset_t,Amt_t,Percentage_t,Char_t,Boolean_t,'
	typeStr = typeStr + 'String_t,MultipleCharValue_t,Currency_t,Exchange_t,Month-Year_t,UTCTimeStamp_t,UTCTimeOnly_t,LocalMktTime_t,'
	typeStr = typeStr + 'UTCDate_t,Data_t,MultipleStringValue_t,Country_t,Language_t,TZTimeOnly_t,TZTimestamp_t,Tenor_t'
	typeVar = typeStr.split(',')

	i = 1
	for t in typeVar:		
		typeDict[t] = str(i)
		i = i+1	
#-------------------------------------------------------------

def validateParameterRefs_BasicParameters(args):
	global isError

	layouts = getLayouts(args)
	for l in layouts:
		parameterRefs = l.getElementsByTagName("lay:control");					
		if not parameterRefs:
			print('No parameterRefs defined under ''basicParameters''. Please verify XML!')
			noFurtherProcessing()
			#----
		for pr in parameterRefs:
			prName = pr.getAttribute('parameterRef')
			if not prName in pRefList:						
				pRefList.append(prName)			
			else:
				if(prName != 'dummy_parameter'):
					print('parameterRef name (='+ prName +') REPEATED under basicParameters')
					print('>>FYI: Parameter name should always be UNIQUE within basicParameters.'+'\n')				
					isError = True
#-------------------------------------------------------------

# this method does the validation of all strategies and builds a valid parameter list per strategy
def processStrategies(args):	

	pName  = ''
	global isError
	global typeDict

	for stgy in args:
		pList = []
		pRefList = []
		sName = stgy.getAttribute('name')

		# print('Processing parameters for strategy '+ sName)
		parameters = getParameters(stgy)
		fixtagValList = []
		pNameList = []

		for p in parameters:
			pName = p.getAttribute('name')

			# check for the type validation, type attribute should match with xsi:type
			if typeDict[p.getAttribute('xsi:type')] != p.getAttribute('type'):
				print('xsi:type attribute of parameter (='+ pName +') does not match with ''type''')
				print('>>FYI: Expected type='+typeDict[p.getAttribute('xsi:type')]+'\n')

			# check for duplicate parameter names
			if not pName in pNameList:
				pNameList.append(pName)
			else:
				print('Parameter name (='+ pName +') REPEATED under strategy ="'+ sName +'"')
				print('>>FYI: Parameter name should always be UNIQUE within a Strategy.'+'\n')				
				noFurtherProcessing()
				#----

			# check for duplicate fixtag
			if not p.getAttribute('fixTag') in fixtagValList:
				fixtagValList.append(p.getAttribute('fixTag'))
			else:
				print('fixTag value (='+p.getAttribute('fixTag')+') REPEATED at parameter="'+ p.getAttribute('name') +'" under strategy ="'+ sName +'"')
				print('>>FYI: fixTag value should always be UNIQUE across all Parameters within a Strategy.'+'\n')				
				noFurtherProcessing()
				#----			

			#validate if parameterType="3" is set
			if(p.getAttribute('parameterType') == '3'):
				print('parameterType=''3'' present under parameter="'+pName+'" \n >>FYI: parameterType should only present for ''basicParameters.''')
				noFurtherProcessing()
				#----

			# validate if contradictory attributes present under same parameter
			if(p.getAttribute('disableOnRplIfTimeExpired') !='' and p.getAttribute('mutableOnCxlRpl') !='' ):
				print('"mutableOnCxlRpl" AND "disableOnRplIfTimeExpired" were specified under same parameter="'+pName+'"')
				noFurtherProcessing()
				#----

			# dummy_parameter parameter should be tagged as -888
			if(pName == 'dummy_parameter'):
				if(p.getAttribute('fixTag') != '-888'):
					print('Invalid fixTag under parameter="'+pName+'" \n >>FYI: fixTag of dummy_parameter should always be -888.')
					noFurtherProcessing()
					#----
			# ignore constants
			if (p.getAttribute('const') == ''):
				if not pName in pList:
					# print('Nonconst parameter: '+ pName)
					pList.append(pName);
			else:
				if(p.getAttribute('xsi:type') != 'String_t'):
					print('Invalid xsi:type under parameter="'+pName+'" \n >>FYI: xsi:type of constant should always be String_t.')
					noFurtherProcessing()
					#----

		if pList:
			layouts = getLayouts(stgy)
			for l in layouts:
				parameterRefs = l.getElementsByTagName("lay:control");					
				if not parameterRefs:
					print('No parameterRefs defined under strategy = "'+ sName +'". Please verify XML!')
					noFurtherProcessing()
					#----
				for pr in parameterRefs:
					prName = pr.getAttribute('parameterRef')
					if not prName in pRefList:
						# print('parameterRefs: '+prName)
						pRefList.append(prName)			
					else:
						if(prName != 'dummy_parameter'):
							print('Parameter reference name (='+ prName +') REPEATED under strategy ="'+ sName +'"')
							print('>>FYI: Parameter name should always be UNIQUE within a Strategy.'+'\n')				
							isError = True

			# validate the parameter definitions
			validateParameterRefs(pList,pRefList,sName)	

			# validate the val:edit definitions for all parameters
			validateValEditRules(stgy,pList,sName)
#-------------------------------------------------------------

def validateValEditRules(args, pList, sName):	
	global isError
	vList =[]

	if not pList:
		parameters = args.getElementsByTagName("parameter")
		for p in parameters:
			if p.getAttribute('const') == '':
				if p.getAttribute('name') not in pList:
					pList.append(p.getAttribute('name'))

	valStratEditList = args.getElementsByTagName('val:strategyEdit')
	if valStratEditList:
		for vl in valStratEditList:
			valEditList = vl.getElementsByTagName('val:edit')	
			if valEditList:
				for ve in valEditList:
					vName = ve.getAttribute('field')
					if (vName not in vList):
						vList.append(vName)				
	
	for v in vList:
		if (v !='' and v not in pList):
			eMsg ='val:edit specified for "'+ v +'" is NOT defined as a parameter' 
			if sName != '':
				eMsg = eMsg + ' under strategy: "' + sName +'"'
			eMsg = eMsg + '.\n'
			eMsg = eMsg + '>>FYI: Edit validations work only on a given parameter.\n'

			print(eMsg)				
			isError = True
#-------------------------------------------------------------

def validateParameterRefs(pList, pRefList,sName):	
	global isError
	for p in pList:		
		if p not in pRefList:
			print(p +' not referenced in parameterRefs for Strategy: '+ sName +'\n')		
			isError = True	
	
	for p in pRefList:
		if p not in pList:
			print(p +' not declared for Strategy: '+ sName+'\n')
			isError = True					
#---------------------------------------------------------------

def parseXML(args):	
	global typeDict

	# Open XML document using minidom parser
	DOMTree = xml.dom.minidom.parse(args)
	collection = DOMTree.documentElement	


	# Get all the basic parameters ------------------------------------------------------------------------
	basicParameters = collection.getElementsByTagName("basicParameter")
	if not basicParameters:
		print('No "<basicParameter>" specified. BIG MISTAKE!')
		noFurtherProcessing()
		#----

	# initialize the dictionary
	typeAttributesDict()

	print('Processing basicparameters ...')
	for bp in basicParameters:		
		bplist = bp.getElementsByTagName('parameter')				
		fixtagValList = []
		for bpp in bplist:						
			bppName = bpp.getAttribute('name')
			# check for the type validation, type attribute should match with xsi:type
			if typeDict[bpp.getAttribute('xsi:type')] != bpp.getAttribute('type'):
				print('xsi:type attribute of parameter (='+ bppName +') does not match with ''type''')
				print('>>FYI: Expected type='+typeDict[bpp.getAttribute('xsi:type')]+'\n')

			if not bpp.getAttribute('fixTag') in fixtagValList:
				fixtagValList.append(bpp.getAttribute('fixTag'))
			else:
				print('fixTag REPEATED at basicparameter="'+ bppName +'"')
				print('>>FYI: fixTag value should always be UNIQUE across all basicParameters.')				
				noFurtherProcessing()
				#----

			if(bpp.getAttribute('parameterType') == ''):
				print('"parameterType" attribute missing under basic parameter="'+  +'"')
				print('>>FYI: parameterType="3" is mandatory for all basic parameters.')				
				noFurtherProcessing()	
				#----
			elif(bpp.getAttribute('parameterType') != '3'):
				print('Invalid parameterType value under basic parameter="'+ bppName +'"')
				print('>>FYI: parameterType="3" is mandatory for all basic parameters.')				
				noFurtherProcessing()
				#----			

		# check if any parameter specific references are missing etc
		validateParameterRefs_BasicParameters(bp)

		# check if val:edit does not have proper parameter reference
		validateValEditRules(bp,[],'')
	#--------------------------------------------------------------------------------------------------------
	
	# Get all the regions 
	regions = collection.getElementsByTagName("region")
	if not regions:
		print('No regions found! Something wrong with XML!');
		noFurtherProcessing()
		#----
	
	for r in regions:
		assetTypesList = []
		strategiesList = []
		regionName = r.getAttribute('name')
		pList = set()
		pRefList = set()

		print('')
		print('Processing region ...'+ regionName)
		assetTypes = getAssetTypes(r)
		if not assetTypes:
			print('No asset classes found, so proceeding with Regions....');
			time.sleep(1);
			strategies = getStrategies(r) # read strategies from region as no asset types are declared
			if strategies:
				processStrategies(strategies)
				validateParameterRefs('Region - ' + regionName)
		else:
			for aType in assetTypes:
				aName = aType.getAttribute('name')
				print('Processing asset type ... '+ aName)				
				strategies = getStrategies(aType) # read strategies from asset types are declared
				if strategies:
					processStrategies(strategies)		
	if isError:
		print('')
		print('VALIDATION ERRORS FOUND. PLEASE VERIFY XML AGAIN!')
	else:
		print(outputMsg)