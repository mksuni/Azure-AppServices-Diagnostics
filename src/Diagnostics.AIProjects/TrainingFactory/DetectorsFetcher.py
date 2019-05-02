import os, json, requests
from ResourceFilterHelper import getProductId
config = json.loads(open("metadata/config.json", "r").read())
class DetectorsFetcher:
    def __init__(self, detectorsUrl):
        self.detectorsUrl = detectorsUrl if detectorsUrl else "http://localhost:{0}/internal/detectors".format(config["internalApiPort"])

    def fetchDetectors(self, productid, datapath):
        content = json.loads(requests.get(self.detectorsUrl).content)
        detectors = [detector for detector in content if (productid in getProductId(detector["resourceFilter"]))]
        for detector in detectors:
            if detector["metadata"]:
                md = json.loads(detector["metadata"])
                detector["utterances"] = md["utterances"] if "utterances" in md else []
            else:
                detector["utterances"] = []
        if len(content)>0:
            try:
                open(os.path.join(datapath, "Detectors.json"), "w").write(json.dumps(detectors, indent=4))
            except:
                pass