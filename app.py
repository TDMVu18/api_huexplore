from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
from time import time
import pandas as pd
from pymongo import MongoClient
import osmnx as ox
from shapely import LineString, Point, Polygon
import random

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["unihack"]
collection = db["locations"]

G = ox.load_graphml('graph.graphml')

def get_place_dict()->dict:
    mongo_results = list(collection.find())
    names_res, coor_res = [], []
    for index, result in enumerate(mongo_results, start=1):
        names_res.append(result["name"])
        coor_res.append(result["coordinate"])
    x = [float(i[1]) for i in coor_res]
    y = [float(i[0]) for i in coor_res]
    place_dict = {}
    for i in range(len(names_res)):
        place_dict[names_res[i]] = {'lat':x[i], 'long':y[i]}  
    return place_dict

place_dict = get_place_dict()

@app.route('/ind-loc', methods = ['POST'])
def get_ind_loc():
    data = request.get_json()

    mongo_results = []
    query = {}
    if data["is_interests"]:
        query["interests"] = {"$all": data["interests_select"]}

    if data["is_moods"]:
        query["moods"] = {"$all": data["moods_select"]}

    names_res, img_res, coor_res, ggmap_res, interests_res, moods_res, node_id = [], [], [], [], [], [], []

    if data["interests_select"] or data["moods_select"]:
        mongo_results = list(collection.find(query))
    
    mongo_results = list(collection.find(query))

    for index, result in enumerate(mongo_results, start=1):
        result["order"] = index
        names_res.append(result["name"])
        img_res.append(result["img_url"])
        coor_res.append(result["coordinate"])
        ggmap_res.append(result["gg_map"])
        interests_res.append(result["interests"])
        moods_res.append(result["moods"])
        node_id.append(result["node_id"])

    return jsonify(
            {
                'names_res':names_res, 
                'img_res': img_res, 
                'coor_res': coor_res, 
                'ggmap_res':ggmap_res, 
                'interests_res': interests_res, 
                'moods_res': moods_res,
                'node_id'   : node_id
                }
            )

@app.route('/dynamic-loc', methods = ['POST'])
def get_dynamic_loc():
    data = request.get_json()

    mongo_results = []
    query = {
        '$or': [
            {'moods': {'$in': data["moods_can"]}},
            {'interests': {'$in': data["interests_can"]}}
        ]
    }
    names_res, img_res, coor_res, ggmap_res, interests_res, moods_res, node_id = [], [], [], [], [], [], []
    mongo_results = list(collection.find(query))
    for index, result in enumerate(mongo_results, start=1):
            result["order"] = index
            names_res.append(result["name"])
            img_res.append(result["img_url"])
            coor_res.append(result["coordinate"])
            ggmap_res.append(result["gg_map"])
            interests_res.append(result["interests"])
            moods_res.append(result["moods"])   
            node_id.append(result["node_id"])
    
    filter_df = candidate_df = pd.DataFrame(
        {'names_res':names_res, 
         'img_res': img_res, 
         'coor_res': coor_res, 
         'ggmap_res':ggmap_res, 
         'moods_res': moods_res,
         'interests_res': interests_res,
          'node_id'   : node_id
         }
    )
    filter_df['geometry'] = [Point(float(place_dict[i]['long']),float(place_dict[i]['lat'])) for i in names_res]
    # List coordinates 
    # place_dict    # (16.4531082, 107.5449069), (16.4512429, 107.4941086), (16.392005, 107.5842296)
    place_routed = data['name_res']
    coords = ((place_dict[i]['long'],place_dict[i]['lat']) for i in place_routed)
    if len(place_routed) > 2:
        # Trên 2 thì vẽ polygon
        polygon = Polygon(coords)
        polygon = polygon.convex_hull.buffer(0.005) # the atribute
    else:
        # Dưới 2 thì tìm địa điểm trên Line
        polygon = LineString(coords)
        polygon = polygon.buffer(0.015)
    filter_df = filter_df[polygon.contains(candidate_df['geometry'])==True]
    filter_df = filter_df[candidate_df.names_res.isin(place_routed) == False]
    near_places = list(filter_df.names_res)
    if len(near_places) > 16:
        near_places=near_places[:17]
    candidate_df['isshow_res'] = candidate_df.names_res.isin(near_places)
    candidate_df = candidate_df.drop(columns='geometry')
    
    return jsonify(candidate_df.to_dict(orient='list'))

@app.route('/check-place-dict', methods = ['GET'])
def check_place_dict():
    return jsonify(place_dict)

@app.route('/find-route', methods = ['POST'])
def find_route():
    data = request.get_json()
    origin_node = data["origin_node"]
    destination_node = data["destination_node"]
    route_nodes = ox.routing.shortest_path(G, origin_node, destination_node, weight="length")
    points_list = [[G.nodes[node]['y'],G.nodes[node]['x']] for node in route_nodes]
    return points_list

if __name__ == "__main__":
    app.run(debug= True)