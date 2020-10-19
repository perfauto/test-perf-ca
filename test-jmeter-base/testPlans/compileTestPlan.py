import xml.etree.cElementTree as ET
import os
import sys

# a utility for replacing IncludeController elements with actual fragment contents in a Jmeter Test plan
# usage: <input jmx> <includes root dir>
def getUsage():
	return 'usage: <input jmx> <includes root dir> <output jmx file>'

expectedArgLength = 3
if len(sys.argv) < expectedArgLength + 1:
	raise Exception('expecting ' + str(expectedArgLength) + ' arguments and received ' + str(len(sys.argv) - 1) + '\n\n' + getUsage())
	
inputJmx = sys.argv[1]
includesDir = sys.argv[2]
outputFile = sys.argv[3]
testPlansDir = os.path.dirname(inputJmx)
print ('using testplan dir=' + str(testPlansDir))
print ('using fragment root dir=' + str(includesDir))

# get the fragment file
def parseJmxFile(fragFile):
	tree = ET.parse(fragFile)
	root = tree.getroot()
	print ('parsed fragFile from=' + fragFile)
	return root

# recursive function for walking the tree
# looks for include controllers and replaces them with a generic controller containing the actual test fragment elements
def replaceIncludeControllers(element):
	count = 0
	fragReplacementMap = []
	for childElement in list(element):
		count = count + 1
		if 'IncludeController' in childElement.tag:
			# convert the element
			# FROM: <IncludeController guiclass="IncludeControllerGui" testclass="IncludeController" testname="logoff"   enabled="true">
			# TO:   <GenericController guiclass="LogicControllerGui"   testclass="GenericController" testname="/ logoff" enabled="true"/>
			childElement.tag = 'GenericController'
			childElement.set('guiclass','LogicControllerGui')
			childElement.set('testclass','GenericController')
			childElement.set('testname', '/ ' + childElement.get('testname'))
			
			# extract the include path
			stringPropEl = childElement.find('stringProp')
			fragFile = stringPropEl.text
			
			# remove the stringProp, it's no longer required
			childElement.remove(stringPropEl)
			
			# parse the testFragment
			print ('found include=' + str(fragFile))
			testFragmentRoot = parseJmxFile(os.path.join(includesDir, os.path.normpath(fragFile)))
			
			# find the first hashTree sibling of the TestFragmentController element (the sibling contains the meat and potatoes of the fragment)
			frag = testFragmentRoot.find('.//TestFragmentController/../hashTree')
			
			# recursive call for the element we just grabbed from the include file
			newElement = replaceIncludeControllers(frag)
			
			# create a map of elements for replacement later (can't modify the thing we are iterating over)
			# Map: index we replace at, old element to replace, new element
			fragReplacementMap.append({'index': count, 'old': childElement, 'new': newElement})

		elif 'JSR223PostProcessor' in childElement.tag:

			# filename stringProp
			filenameEl = childElement.find('stringProp[@name="filename"]')
			filename = filenameEl.text

			# if filename is populated, read file and encode as script body
			if filename:
				# adjust filename
				filename = filename.replace('${__P(includecontroller.prefix)}',includesDir);

				# read file contents
				scriptAsString = open(filename,mode='r').read()

				# replace script text
				scriptEl = childElement.find('stringProp[@name="script"]')
				scriptEl.text = scriptAsString

				# blank out the filename
				filenameEl.text = ''

		else:
			# not an include, curse over the children
			replaceIncludeControllers(childElement)
			
	# now we can do the replacements
	for rep in fragReplacementMap:
		index = rep['index']
		elementToReplace = rep['old']
		newElement = rep['new']
		
		# there is always an empty <hastTree /> following the IncludeController, time to remove it since we are replacing it
		emptyHashTree = element[index]
		element.remove(emptyHashTree)
		
		# put in the new element
		element.insert(index, newElement)
		print ('replaceMap = ' + elementToReplace.tag + ',' + str(index) + ',' + newElement.tag)

	return element

# parse the input jmx file 
tree = ET.parse(inputJmx)
root = tree.getroot()

# walk the entire tree, looking for include controllers and replacing them with a generic controller containing the actual test fragment
root = replaceIncludeControllers(root)

# save it
tree.write(os.path.normpath(outputFile))
print ('done.')