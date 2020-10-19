import groovy.json.JsonSlurper

itemVarName = args[0]
itemDatacheckKeyName = args[1]
datacheckVariableName = args[2]

item = new JsonSlurper().parseText(vars.get(itemVarName))
datachecks = item[itemDatacheckKeyName]

// if it's a map then we have specific datachecks per version of product
if (datachecks instanceof groovy.json.internal.LazyMap) {

	// must treat datachecks as a multiversion map
     datachecks_mv = datachecks

     // sort the release versions available but skip "default"
	sortedListOfDefinedVersions = []
	for(key in datachecks_mv.keySet()) {
		if ("default".equals(key)) continue // skip
		
		// only care about release version
		key_releaseVersion = key
		sortedListOfDefinedVersions.add(Integer.parseInt(key_releaseVersion.minus(".").minus(".")))
	}
	sortedListOfDefinedVersions = sortedListOfDefinedVersions.sort()

	currentCandidate = 0
	// iterate over sorted list
	for(key in sortedListOfDefinedVersions) {
		
		// looking for lowest key that's >= the release
		if (Integer.parseInt(vars.get("productVerKey").toString()) >= key && key > currentCandidate) {
			currentCandidate = key
			datachecks = datachecks_mv[key_releaseVersion.toString()]
			//log.info("PRODUCT COMPARISON " + vars.get("productVerKey").toString() + " : " + key.toString() + " : " + currentCandidate.toString() + " : " + key_releaseVersion.toString())
		} else {
			// since it's a sorted list, no point in searching further
			break;
		}
	}
	if (currentCandidate == 0) {
		// no newer candidate found use default
		datachecks = datachecks_mv["default"]
	}
}

// create jmeter friendly array variable
datacheckCount = 0
for(datacheck in datachecks) {
	datacheckCount++
	vars.put(datacheckVariableName + "_" + datacheckCount, datacheck.toString())
	vars.put(datacheckVariableName + "_matchNr", String.valueOf(datacheckCount))
}
