# Sample JMeter scripts for CA functionality

This package is provided as-is, without support, to exercise some basic functionality in IBM Cognos Analytics (CA) 11.1.2 to 11.1.7. 

This document will show how to run a simple perf test using Base Samples in CA. 

## Table of Contents
  * [Prerequisites](#prerequisites)
  * [Setup](#setup)
    * [Authentication](#authentication)
      * [Default](#default)
      * [Custom LDAP](#custom-ldap)
      * [Custom Authentication Provider](#custom-authentication-provider)
    * [chromedriver](#chromedriver)
    * [CA Content](#ca-content)
      * [Using CA Samples](#using-ca-samples)
      * [Custom Content](#custom-content)
    * [defining a custom scenarioFile](#defining-a-custom-scenariofile)
  * [Usage](#usage)
  * [Examples](#examples)
    * [Single user uploading a file for 1 iteration](#single-user-uploading-a-file-for-1-iteration)
    * [compile script for multi-user tests](#compile-script-for-multi-user-tests)
    * [run multi-user test](#run-multi-user-test)
  * [Results](#results)
  * [Best Practices](#best-practices)
    * [use a compiled test plan](#use-a-compiled-test-plan)
    * [many concurrent logins with same username](#many-concurrent-logins-with-same-username)
  * [FAQ - Frequently Asked Questions](#faq---frequently-asked-questions)
    * [What is “oid” in the samples.json?](#what-is-oid-in-the-samplesjson)
    * [When should we use “prompt” parameter?](#when-should-we-use-prompt-parameter)
    * [Action sections in the samples.json seem to have the same content as the items sections. What is the difference?](#action-sections-in-the-samplesjson-seem-to-have-the-same-content-as-the-items-sections-what-is-the-difference)
    * [What does chartcount represent and where do we get its value from?](#what-does-chartcount-represent-and-where-do-we-get-its-value-from)
  * [Troubleshoot](#troubleshoot)
    * [Proxy JMeter](#proxy-jmeter)
    * [Dashboard Recording Files](#dashboard-recording-files)
      
## Prerequisites
 * some knowledge of [JMeter](https://jmeter.apache.org)
 * 64-bit version of Java, 1.8 or later
 * python 2.7 or later (if modifying test fragments)
 * chrome and corresponding chromedriver

## Setup
### Authentication
#### Default
The scripts default to using annonymous login if enabled, otherwise uses the following credential pattern:
   * CAMUsername=`${__P(usernamePrefix,user)}${__threadNum}`
   * CAMPassword=`cognos`
   * CAMNamespace=`${__P(namespace,LDAP)}`

Using the above, the first trio of authentication parameter values would be user1,cognos,LDAP

#### Custom LDAP
CA configured with a custom LDAP. See [Configuring IBM Cognos components to use LDAP](https://host.com/support/knowledgecenter/SSEP7J_11.1.0/com.ibm.swg.ba.cognos.inst_cr_winux.doc/t_ldapauthentication_process-element.html)

Create a **tabbed** delimited file containing three columns: CAMUsername,CAMPassword and CAMNamespace. For a sample use [/test-jmeter-base/testPlans/credentialFile.csv]. Supply the file to jmeter via the credentialFile parameter `credentialFile`. i.e `-JcredentialFile=/tmp/creds.csv`

#### Custom Authentication Provider
Authentication is handled in `test-jmeter-ca-all/testFragments/cognos_analytics/common/bi_login.jmx`. It is recommend this file be modified in place.

A custom `bi_login.jmx` must do the following:
  * call `common/bi_connect.jmx`
  * set the user variable `cafContextId` (typically comes from CA response of authenticated GET on `/bi/v1/login`)
  * set the user variable `loggedOn=true`

Corresponding clean up logic specific to the custom authentication provider should be put in `test-jmeter-ca-all/testFragments/cognos_analytics/common/bi_logoff.jmx`

### chromedriver
If exercising Dashboards or Stories, the `[Setup - Record] Open dashboards to get querySpecs` setup thread group invokes a chromedriver to record http calls for later playback in the main thread group. This requires chrome and the corresponding chromedriver to be available. Make sure to use a chromedriver that supports the chrome version: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

Sample setup on RHEL:
1. `curl --remote-name https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm`
2. `yum -y install ./google-chrome-stable_current_x86_64.rpm`
3. ``curl --remote-name https://chromedriver.storage.googleapis.com/`curl -k https://chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip``
4. supply full path to chromedriver via jmeter property `chromedriver` i.e. `-Jchromedriver=/tmp/chromedriver`

### CA Content
#### Using CA Samples
Import Samples_for_Install_*.zip deployment into CA (See [Base Samples for IBM Cognos Analytics](https://host.com/community/user/businessanalytics/blogs/steven-macko/2018/09/12/base-samples-for-ibm-cognos-analytics))

Use the jmeter property `scenarioFile` to set the input json to the corresponding samples deployment version. i.e. `-JscenarioFile=test-jmeter-base/testPlans/samples_11.1.7.json`. Input files are available here: `test-jmeter-base/testPlans/samples*.json`

#### Custom Content
Custom content can be exercised by defining artifacts in supplied `scenarioFile` in json format. Use the json available at `test-jmeter-base/testPlans/samples*.json` as refernce for writing. Make sure to use a json validator before trying to use it (i.e. `python -m json.tool` or `json-glib-format`)

For more details, see [defining a custom scenarioFile](#defining-a-custom-scenariofile) below

### defining a custom scenarioFile
The scenarioFile is the file containing json that defines the test scenarios that can be executed. Open one of the samples*.json in an editor and look for this scenario called “SampleReport”: 
```
{
  "scenarioGroup": "SampleReport",
  "scenarios": [
    {
      "items": [
        {
          "chartcount": "2",
          "datacheck": "Telephone",
          "name": "Global sales",
          "type": "report"
        }
      ],
      "navigation": "Samples,Reports",
      "scenario": "SampleReport"
    }
  ]
}
```
The json entries:  
  * `navigation` defines the navigation path to the object in Cognos Analytics. Assumed to be under "Team Content". 
  * `type` defines what object type is executing: report, dashboard, fileupload, etc. (controlled via `test-jmeter-ca-all/testFragments/cognos_analytics/launch.jmx`)
  * `name` defines the defaultName of the object to be executed.  
  * `datacheck` represents a value from the response used as a string assertion.
  
Many more items can be used for additional actions or verification.  

A multi-tab dashboard example can be seen below: 
```
{
  "scenarioGroup": "samples_product_line_dash_4tabs",
  "scenarios": [
    {
      "items": [
        {
          "actions": [
            {
              "datachecks": [
                "Department Store",
                "Packs"
              ],
              "name": "Product",
              "suggestions": 0,
              "type": "nextTab"
            },
            {
              "datachecks": [
                "United Kingdom",
                "Eyewear Store",
                "Canada"
              ],
              "name": "Retailer",
              "suggestions": 0,
              "type": "nextTab"
            },
            {
              "datachecks": [
                "Equipment",
                "Mail"
              ],
              "name": "Order Method",
              "suggestions": 1,
              "type": "nextTab"
            }
          ],
          "datacheck": [
            "2015",
            "Golf Equipment",
            "Golf Shop",
            "Web"
          ],
          "name": "Product line dashboard",
          "suggestions": 2,
          "type": "dashboard"
        }
      ],
      "navigation": "Samples,Dashboards",
      "scenario": "samples_product_line_dash_4tabs"
    }
  ]
}
```
A file upload example can be seen below: 
```
{
  "comments": " Group of Files ",
  "scenarioGroup": "bulk_upload_Samples",
  "scenarios": [
    {
      "items": [
        {
          "name": "Samples",
          "type": "file_upload"
        }
      ],
      "scenario": "bulk_upload_Samples"
    }
  ]
}
```
All test cases must be defined in a  json.  Please study the samples.json to see other examples. 

## Usage
This describes the general usage of the scenariogroup_run.jmx test plan.
|Parameter       |Required |Default    |Description
|----------------|:-------:|-----------|-----------|
|server          |Yes      |           |server part of URL i.e. http[s]://server[:port][/alias]/bi/ |
|port            |Yes      |           |port part of URL i.e. http[s]://server[:port][/alias]/bi/ |
|protocol        |Yes      |           |protocol being used `http` or `https` |
|urlPath         |Yes      |           |urlPath part of URL i.e. http[s]://server[:port][/urlPath]/bi/ |
|users           |No       |1          |number of concurrent virtual users |
|iteration       |one of iteration or duration|0          |number of iterations each user will run |
|duration        |one of iteration or duration|0          |number of seconds each user will run |
|scenario        |No       |1widget_bubble_chart_csv_1000rows100cols_2tabs |scenarioGroup used for lookup in the scenarioFile |
|scenarioFile    |Yes      |test-jmeter-base/testPlans/scenarios.json|scenarios.json does not exist. Must exist relative to [/test-jmeter-base/testPlans/](test-jmeter-base/testPlans). Look there for Samples_*.json|
|credentialFile  |No       |user1/cognos|A tab delimited file (username\tpassword\tnamespace). For sample use [/test-jmeter-base/testPlans/credentialFile.csv](/test-jmeter-base/testPlans/credentialFile.csv). See [#ca-authentication](#ca-authentication) for more details.|
|namespace       |No       |LDAP          |namespace name to use for login if credentialFile not used. |
|recordingEnabled|No       |1 |1 to record. 0 to skip recording. |
|recordingDir    |No       |test-jmeter-ca-all/recordings/|A writable location used for recordings.|
|icp4d           |No       |false      |When testing against CA-Addon in icp4d use `true`|

## Examples
### Single user uploading a file for 1 iteration
```
./run.sh -n -t test-jmeter-base/testPlans/scenariogroup_run.jmx \
 -Jserver=$serverName -Jport=$serverPort -Jprotocol=https \
 -Jscenario=CSV_25000rows25cols -Jusers=1 -Jiteration=1 \
 -JscenarioFile=test-jmeter-base/testPlans/samples_11.1.7.json \
 -l samples.jtl -j jmeter.log -JresponseErrorFile=errors.xml 
```
Note: to launch the JMeter GUI drop the `-n` 

### compile script for multi-user tests
There is a "compiled" version of the scenariogroup_run.jmx available. If you tend to have an aggressive ramp-up (< 60s), then it is a good idea, for performance reasons, to use the "compiled" version of the test plan. There is a compile script (requires python) that must be run any time a modification to a test fragment is made.
```
cd test-jmeter-ca-all/compiledTestPlans
./compile.bat or ./compile.sh
```
Then use `-t test-jmeter-ca-all/compiledTestPlans/scenariogroup_run.jmx` to use the compliled test plan.

### run multi-user test
NOTE the use of a compiled test plan. see above.
This runs 5 users for 5 iterations. Each user uploads a file 5 times. Test is run in non-gui mode.
```
./run.sh -n -t test-jmeter-base/compiledTestPlans/scenariogroup_run.jmx \
 -Jserver=$serverName -Jport=$serverPort -Jprotocol=https \
 -Jscenario=CSV_25000rows25cols -Jusers=5 -Jiteration=5 \
 -JscenarioFile=test-jmeter-base/testPlans/samples_11.1.7.json \
 -l samples.jtl -j jmeter.log -JresponseErrorFile=errors.xml 
```

## Results
Please refer to JMeter documentation for reporting and analysis of results. A good starting place: [generating-dashboard](https://jmeter.apache.org/usermanual/generating-dashboard.html)

## Best Practices
### use a compiled test plan
JMeter utilizes a significant amount of resources at startup trying to include fragments dynamically. If thread count is low (<10) or if ramp-up period is large (>60s) this may not be an issue. Otherwise, it is a good practice to utilize the compile script noted above [compile script for multi-user tests](#compile-script-for-multi-user-tests)

### many concurrent logins with same username
If using annonymous or concurrent logins with the same username, it is good practice to disable all the `/bi/v1/users/~/mrus` HTTP requests in both the `bi_login.jmx` and the `bi_logoff.jmx` test fragments. 

## FAQ - Frequently Asked Questions
### What is “oid” in the samples.json?
The oid doesn’t matter anymore. It is there for historical purposes. Setting it blank for everything is fine.  

### When should we use “prompt” parameter? 
The prompt parameter is for reports with a prompt page. You put the name of the prompt and the value you want to select.  
More examples of prompts can be found in the promptExamples.txt file.  

### Action sections in the samples.json seem to have the same content as the items sections. What is the difference?  
Think of items as the thing you’re working with (ie. report or dashboard). By default the script opens the item and those are the values listed in the items section. Actions are what you want to do with the item after you’ve opened it. For example for a report an action you might want to do after opening it is a “nextPage” or “lastPage”.  

### What does chartcount represent and where do we get its value from?  

Chartcount is the number of charts on the report page. This can typically be grabbed by looking at the report through the browser manually. Also if the script is run with chartcount=0 and there are charts found the script will fail with a message like “chart count = 0 but 3 charts returned.”  

## Troubleshoot
### Proxy JMeter
You can run the JMeter with the requests going through a proxy by supplying the parameters `proxyHost` and `proxyPort`. 

### Dashboard Recording Files 

By default dashboard test case recording files are saved to this directory structure: test-jmeter-ca-all/testFragments/cognos_analytics/data.  It is good practice to delete this folder when testing against a new version of Cognos or a new Content Store. If you are having issues with the dashboard test cases the first thing to try would be to delete the data (or data folder) and its contents.  

The contents of the folder (if there are any) should match your Team Content folder structure for the Dashboard test cases you are trying to run. The data folder is being defined by the "data_dir" parameter in the "test parameters" section. 
