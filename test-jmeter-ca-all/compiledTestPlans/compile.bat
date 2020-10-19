SET local
SET currentDir=%~dp0
SET fragmentDir=%currentDir%..\testFragments\cognos_analytics
SET sourceTestPlanDir=%currentDir%..\..\test-jmeter-base\testPlans
SET compileScript=%sourceTestPlanDir%\compileTestPlan.py

:: The batch script checks whether it is using python2, if Python2 is not found, it sets the batch
:: script to run on python3. If neither work, make sure to check that the environment variable is 
:: correctly setup.
SET pythonCmd=python -3

where pythonCmd
if NOT ERRORLEVEL 0 (
	set pythonCmd=python
) 

where pythonCmd
if NOT ERRORLEVEL 0 (
	echo ERROR: Failed to find a python interpreter
)

for /F %%i in (%currentDir%\testPlanList.txt) do (
	call %pythonCmd% %compileScript% %sourceTestPlanDir%\%%i %fragmentDir% %currentDir%\%%i
)