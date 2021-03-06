import json, os, gensim
from gensim.similarities import WmdSimilarity
from pyemd import emd
from SearchModule.ModelInfo import ModelInfo
from SearchModule.TokenizerModule import getAllNGrams
from SearchModule.Exceptions import *
from SearchModule.Utilities import absPath, verifyFile
from SearchModule.MessageStrings import fileMissingMessage

class WmdSearchModel:
    def __init__(self, modelpackagepath):
        packageFiles = {
            "m1IndexFile": "m1.index",
            "m2IndexFile": "m2.index",
            "detectorsFile": "Detectors.json",
            "sampleUtterancesFile": "SampleUtterances.json",
            "mappingsFile": "Mappings.json",
            "modelInfo": "ModelInfo.json"
        }
        for key in packageFiles.keys():
            packageFiles[key] = absPath(os.path.join(modelpackagepath, packageFiles[key]))
        self.packageFiles = packageFiles
        self.optionalFiles = ["mappingsFile"]

        if not self.verifyModelFiles():
            raise ModelFileVerificationFailed(fileMissingMessage)

        self.models = {"m1Index": None, "m2Index": None, "detectors": None, "sampleUtterances": None, "mappings": None, "modelInfo": None}
        try:
            with open(self.packageFiles["modelInfo"], "r") as fp:
                self.models["modelInfo"] = ModelInfo(json.loads(fp.read()))
                fp.close()
        except:
            self.models["modelInfo"] = ModelInfo({})
        try:
            self.models["m1Index"] = WmdSimilarity.load(self.packageFiles["m1IndexFile"])
        except:
            raise ModelFileLoadFailed("Failed to load index from file " + self.packageFiles["m1IndexFile"])
        try:
            self.models["m2Index"] = WmdSimilarity.load(self.packageFiles["m2IndexFile"])
            self.models["m2Index"] = None
            del self.models["m2Index"]
        except:
            raise ModelFileLoadFailed("Failed to load index from file " + self.packageFiles["m2IndexFile"])
        try:
            with open(self.packageFiles["detectorsFile"], "r") as f:
                self.models["detectors"] = json.loads(f.read())
                f.close()
        except:
            raise ModelFileLoadFailed("Failed to parse json from file " + self.packageFiles["detectorsFile"])
        if self.models["modelInfo"].detectorContentSplitted:
            try:
                with open(self.packageFiles["mappingsFile"], "r") as f:
                    self.models["mappings"] = json.loads(f.read())
                    f.close()
            except:
                raise ModelFileLoadFailed("Failed to parse json from file " + self.packageFiles["mappingsFile"])
        try:
            with open(self.packageFiles["sampleUtterancesFile"], "r") as f:
                self.models["sampleUtterances"] = json.loads(f.read())
                f.close()
                self.models["sampleUtterances"] = None
                del self.models["sampleUtterances"]
        except:
            raise ModelFileLoadFailed("Failed to parse json from file " + self.packageFiles["sampleUtterancesFile"])
    
    def verifyModelFiles(self):
        for key in self.packageFiles.keys():
            if key not in self.optionalFiles and not verifyFile(self.packageFiles[key], absolute=True, prelogMessage="WmdSearchModel: "):
                return False
        return True

    def getDetectorByIndex(self, index):
        detector = [x for x in self.models["mappings"] if (x["startindex"] <= index <= x["endindex"])]
        if detector and detector[0]:
            return detector[0]["id"]
        else:
            return None

    def queryDetectors(self, query=None):
        if query:
            try:
                tokenized = getAllNGrams(query, self.models["modelInfo"].textNGrams, lemmatize=False)
                similar_doc_indices = sorted(enumerate(self.models["m1Index"][tokenized]), key=lambda x: x[1], reverse=True)[:10]
                if self.models["modelInfo"].detectorContentSplitted:    
                    similar_docs = []
                    for x in similar_doc_indices:
                        detector = self.getDetectorByIndex(x[0])
                        if detector and (not (detector in [p["detector"] for p in similar_docs])):
                            similar_docs.append({"detector": self.getDetectorByIndex(x[0]), "score": str(x[1])})
                else:
                    similar_docs = list(map(lambda x: {"detector": self.models["detectors"][x[0]]["id"], "score": str(x[1])}, similar_doc_indices))
                return {"query": query, "results": similar_docs}
            except Exception as e:
                return {"query": query, "results": [], "exception": str(e)}
        return None

    def loadUtteranceModel(self):
        self.models["m2Index"] = WmdSimilarity.load(self.packageFiles["m2IndexFile"])
        with open(self.packageFiles["sampleUtterancesFile"], "r") as f:
            self.models["sampleUtterances"] = json.loads(f.read())
            f.close()

    def unloadUtteranceModel(self):
        del self.models["m2Index"]
        del self.models["sampleUtterances"]

    def queryUtterances(self, query=None, existing_utterances=[]):
        if query:
            query = query + " ".join(existing_utterances)
            self.loadUtteranceModel()
            try:
                tokenized = getAllNGrams(query, self.models["modelInfo"].textNGrams, lemmatize=False)
                similar_doc_indices = sorted(enumerate(self.models["m2Index"][tokenized]), key=lambda item: -item[1])
                similar_doc_indices = [x for x in similar_doc_indices if self.models["sampleUtterances"][x[0]]["text"].lower() not in existing_utterances][:10]
                similar_docs = list(map(lambda x: {"sampleUtterance": self.models["sampleUtterances"][x[0]], "score": str(x[1])}, similar_doc_indices))
                return {"query": query, "results": similar_docs}
            except Exception as e:
                return {"query": query, "results": None}
            self.unloadUtteranceModel()
        return None