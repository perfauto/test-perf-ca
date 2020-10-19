#!/bin/bash

currentDir=$(pwd)
fragmentDir=$currentDir/../testFragments/cognos_analytics
sourceTestPlanDir=$currentDir/../../test-jmeter-base/testPlans
compileScript=$sourceTestPlanDir/compileTestPlan.py

# The batch script checks whether it is using python2, if python2 is not
# found, it sets the batch script to run python3. If neither works, make sure
# to check that the environment variable is correctly setup.
pythonCmd=python3

which $pythonCmd
if [ $? -ne 0 ];then pythonCmd=python;fi

which $pythonCmd
if [ $? -ne 0 ];then 
	echo ERROR: Failed to find a python interpreter
	exit 1
fi

for testPlan in `cat $currentDir/testPlanList.txt` ; do
    $pythonCmd $compileScript $sourceTestPlanDir/$testPlan $fragmentDir $currentDir/$testPlan
done