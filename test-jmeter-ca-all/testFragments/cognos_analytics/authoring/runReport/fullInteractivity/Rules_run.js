with (JavaImporter(Packages.com.ibm.test.httpdiff)) {
// Rules for httpd: run report in advanved viewer
Rules.setExclusionHeaderNames(new Array("Content-Length", "Cookie", "Cookie2", "Referer", "Host", "If-None-Match", 
"If-Modified-Since", "DNT"))
Rules.setDynamicHeaderNames(new Array(
	"X-XSRF-TOKEN",
	"authenticityToken",
	"cafContextId"
	));

Rules.setExclusionGetSuffixes(new Array(".js", ".gif", ".css", ".png", ".jpg", ".svg", ".xml", 
".dtd", ".woff2", ".htm", "notifications", 
"i083C3A81B1AE44108EB15BF30C3BD168", // exclude some content gets
"8v8Gvs4jCvyw2w29yyGl8yd4448dC9MvGhvw4v2d", // exclude some specific async conversation pieces
"stubbed",
"fmmodels", 
"498hvClwl22ls92Mdqd4wlsG4GMwh24vjMCGyG4d", // exclude some specific async conversation pieces
":443", "success.txt"))

// use these to verify a specific part of the flow i.e. run vs metadata 
//Rules.setExclusionPostSuffixes(new Array("reports"))
//Rules.setExclusionPostSuffixes(new Array("disp"))

Rules.setExclusionQueryParamNames(new Array("f", "k", "s", "rsid", "did"))

Rules.setExclusionFormParamNames(new Array(
	"cv.actionState", "executionParameters", "m_tracking", "ui.cafcontextid", "ui.conversation", "dojo.preventCache"))
	
function filterDynamicValuesFromXml(xml, nodes) {
	for (x in nodes) {
		nodeStart = "<" + nodes[x];
		start = xml.indexOf(nodeStart);
		if (start != -1) {
			valueStart = xml.indexOf('>', start) + 1;
			valueEnd = xml.indexOf('<', valueStart) - 1;
			res = xml.substr(0, valueStart)
			res += Rules.getDynamicValueStub()
			res += xml.substr(valueEnd + 1);
			xml = res;
		}
	}
	return xml;
}

function handleXml(xml) {
	xml = xml.replaceAll("><", ">\n<");
	xml = filterDynamicValuesFromXml(xml, ["contextID", "authenticityToken", "bus:id", "bus:nodeID", "bus:processID", "bus:requestContext", "bus:sessionContext", "bus:stateData"]);
	
	xml = xml.replace(/\t/g, "");
	return xml;
};
Rules.setHandlePostDataTextFunction("handleXml");
}