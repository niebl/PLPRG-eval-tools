#!/usr/bin/python3

import sys
from sklearn.cluster import DBSCAN #newBSD. non-copyleft, GPL compatible TODO: check dependencies.

from models import *
from scoringTypes import *
import uuid
import math
import argparse

'''
#old one
class Trajectory:
    #temporary
    def __init__(self, coordinates):
        self.coordinates = coordinates
'''

class InferenceEngine:
    def __init__(self):
        self.scorings = [
            NightnessScoring(),
            WorkHoursScoring(),
            PointCountScoring()
        ]
        return

    #TODO: IInferenceScoring[]. think about how to implement this.
    #TODO
    def infer(self, trajectory, inferences):
        # cluster Data
        indexClusters = self.cluster(trajectory)
        pointClusters = self.indexClustersToPointClusters(indexClusters,trajectory)

        inferenceResults = []
        #for each cluster...
        for cluster in pointClusters:
            #check all inferences
            for inference in inferences:
                #apply the scorings
                inferenceScores = [] #array of dicts that are results (see scoring defs)
                for scoring in self.scorings:
                    score = scoring.score(cluster, pointClusters)
                    inferenceScores.append(score)
                #interpret scorings
                #print(inference)
                inferenceResult = self.interpretInferenceScores(
                    inference,
                    inferenceScores,
                    cluster,
                    trajectory.id
                )
                if inferenceResult is not None:
                    inferenceResults.append(inferenceResult)
        
        return inferenceResults

    #TODO
    # InferenceDef
    # InferenceScoringResult: List of InferenceScoring Objects (defined in types.py)
    def interpretInferenceScores(self, inferenceDef, scoringResults, cluster, trajectoryId):
        confidences = [] #array of pairs (number, weight)
        for scoringResult in scoringResults:
            #print(scoringResult)
            config = inferenceDef.getScoringConfig(scoringResult["type"])
            if config is not None:
                #print(config)
                #inferenceConfidence = config["confidence"] if config["confidence"] else 0
                inferenceConfidence = scoringResult["value"]
                scoringConfidence = {
                    "confidence": inferenceConfidence,
                    "weight": config["weight"]
                }
                confidences.append(scoringConfidence)

        avgConfidence = 0
        sumWeights = 0
        for conf in confidences:
            sumWeights = sumWeights + conf["weight"]

        if len(confidences) > 0 and sumWeights > 0:
            for conf in confidences:
                avgConfidence += conf["confidence"] * conf["weight"]
            avgConfidence = avgConfidence / sumWeights

        centroid = self.calculateCentroid(cluster)

        #convexhull is being left out for now.

        #return the inference.
        inferenceId = uuid.uuid4()
        return Inference(
            inferenceId,
            inferenceDef.type,
            inferenceDef.type,
            trajectoryId,
            centroid[0],
            [centroid[0]], #this is where the convexHull would go
            confidence=avgConfidence,
            accuracy=centroid[1] #centroid maxDistance
        )

    '''
    TODO: implement trajectory object
    cluster method
    param: Trajectory object
    return: array [clusters, noise]
    '''
    def cluster(self, trajectory, eps=2/6371, min_samples=7):
        #for use of haversine, consider these:
        # https://stackoverflow.com/questions/47206563/sklearn-dbscan-to-cluster-gps-positions-with-big-epsilon
        # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise_distances.html#sklearn.metrics.pairwise_distances
        dbscan = DBSCAN(
            metric = 'haversine',
            eps = eps,
            min_samples = min_samples
        ).fit(trajectory.coords)

        return dbscan.labels_#[i]
        '''
        clusters = []
        noise = []
        print(dbscan.labels_)
        for label in dbscan.labels_:
            if len(clusters)-1 < label:
                clusters.append([])

        for i, point in enumerate(trajectory.coords):
            if dbscan.labels_[i] == -1:
                noise.append(point)
            else:
                clusters[dbscan.labels_[i]].append(point)
        '''

    #TODO: implement the attributes other than latlng
    def indexClustersToPointClusters(self, labels, trajectory):
        clusterList = []
        noise = []

        for label in labels:
            #create clusters in clusterList
            if len(clusterList)-1 < label:
                clusterList.append([])
        
        for i, point in enumerate(trajectory.coords):
            if labels[i] >= 0:
                #create slice
                timeSlice = Point(
                    point, 
                    trajectory.timestamps[i], 
                    trajectory.accuracy[i],
                    trajectory.speed[i]
                    )
                #append slice to cluster in list
                clusterList[labels[i]].append(timeSlice)#

        for cluster in clusterList:
            fC = f'''{{
    "type": "FeatureCollection",
    "features": {cluster}
}}'''
            #print(fC)
        return clusterList

    '''
    calculates a centroid of a given array of points in space
    param: cluster, array of [lon,lat] pairs
    return: array [centerPoint [lon,lat] array, maxDistance]
    '''
    def calculateCentroid(self, cluster):
        if len(cluster) == 0:
            return None
        latSum = 0
        lonSum = 0
        for point in cluster:
            latSum += point.latLon[0] #TODO: investigate whether Poiht flips these around
            lonSum += point.latLon[1]
        centerPoint = [latSum/len(cluster),lonSum/len(cluster)]
        
        maxDistance = 0
        for point in cluster:
            dist = self.haversineDistance(centerPoint, point.latLon)
            if dist > maxDistance:
                maxDistance = dist
                
        centerPointLonLat = [centerPoint[1],centerPoint[0]]
        return (centerPointLonLat, maxDistance)
    
    '''
    implementation of haversine distance in meters
    points are (lat,lon) WGS84
    used this solution: https://stackoverflow.com/a/4913653
    '''
    def haversineDistance(self, p1, p2):
        earthRadius = 6371000 #meters
        dlon = p2[1] - p1[1]
        dlat = p2[0] - p1[0]
        a = math.sin(dlat/2)**2 + math.cos(p1[0]) * math.cos(p2[0]) * math.sin(dlon/2)**2
        c = None
        try:
            c = 2 * math.asin(math.sqrt(a))
        except:
            print("a:")
            print(a)
            print("dlat, dlon:")
            print(f'{dlat}  {dlon}')
            print("p1, p2")
            print(f'{p1}  {p2}')
        distance = c*earthRadius
        return distance

class TimeSlice:
    def __init__(self, latLon, time=None, accuracy=None, speed=None):
        self.latLon = latLon
        self.time = time
        self.accuracy = accuracy
        self.speed = speed
        return
    
    def __repr__(self):
        return str(self.latLon)

#TODO: types.ts
#TODO: nightness-scoring, workHoursScoring, PointCountScoring
#TODO: IinferenceScoring, inferencescoringResult

#TODO: implement other data into the cluster() output so clusterScoring can work with those.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="perform inference attack on geojson inputs")
    parser.add_argument('--file', help='path to a geojson file')
    args = parser.parse_args()

    inputJSON = ""

    trajectory = None
    if not args.file:
        for line in sys.stdin:
            inputJSON += line + "\n"
        trajectory = Trajectory.fromGeoJSON(inputJSON)
    else:
        trajectory = Trajectory.fromGeoJSONfile(args.file)
    
    ie = InferenceEngine()

    inferenceDefinitions = [ #inferenceDefinition. the parameters for the inference
        InferenceDefinition("nightness", 1, 0.3),
        InferenceDefinition("workHours9to5", 1, 0.3),
        InferenceDefinition("pointCount", 1, 0.3)
    ]
    inferences = ie.infer(trajectory, inferenceDefinitions)

    #assign inferences to POIs
    pois = []
    for inference in inferences:
        poiExists = False

        inferenceObj = {
            "id":str(inference.id),
            "type": inference.type,
            "confidence": inference.confidence,
            "accuracy": inference.accuracy
        }

        for poi in pois:
            if poiExists:
                break
            if poi["coords"] == inference.latLon:
                poiExists = True
                poi["inferences"].append(inferenceObj)
                continue

        if not poiExists:
            pois.append({
                "coords": inference.latLon,
                "trajectoryID": str(inference.trajectoryID),
                "inferences": [inferenceObj]
            })

    #create Features of POIs
    poiFeatures = []
    for poi in pois:
        feature = {
            "type": "Feature",
            "properties": poi,
            "geometry": {
                "coordinates": poi["coords"],
                "type": "Point"
            }
        }
        poiFeatures.append(feature)
        

    featureCollection = {
        "type": "FeatureCollection",
        "features": poiFeatures
    }
    outString = json.dumps(featureCollection, indent=4)
    print(outString)
