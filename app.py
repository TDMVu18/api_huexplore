from flask import Flask, request, jsonify
from pymongo import MongoClient
import pandas as pd
from time import time
import pandas as pd
from pymongo import MongoClient
import osmnx as ox
from shapely import Point
import geopandas as gpd

app = Flask(__name__)


client = MongoClient("mongodb://localhost:27017")
db = client["unihack"]
collection = db["locations"]
# G = ox.load_graphml('graph.graphml')

# def filter_candidate_locations(df):
#     return df

# #### Lấy place từ db -> ex: {"Đại Nội": {'lat':16.2, 'long':107.4}} 
# def place_dict()->dict:
#     ggres =  bruh
#     name_list = [i['name'] for i in ggres]
#     geometry = [Point(float(i['coordinate'][0]),float(i['coordinate'][1])) for i in ggres]
#     x = [float(i['coordinate'][1]) for i in ggres]
#     y = [float(i['coordinate'][0]) for i in ggres]
#     place_dict = {}
#     for i in range(len(name_list)):
#         place_dict[name_list[i]] = {'lat':x[i], 'long':y[i]}
#     return place_dict

# #### Lấy Fnb từ db -> ex: {"Phở": {'lat':16.2, 'long':107.4}} 
# def fnb_dict()->dict:
#     ggres =  bruh
#     name_list = [i['name'] for i in ggres]
#     geometry = [Point(float(i['coordinate'][0]),float(i['coordinate'][1])) for i in ggres]
#     x = [float(i['coordinate'][1]) for i in ggres]
#     y = [float(i['coordinate'][0]) for i in ggres]
#     place_dict = {}
#     for i in range(len(name_list)):
#         place_dict[name_list[i]] = {'lat':x[i], 'long':y[i]}
#     return place_dict

# ### Tạo GeoDataFrame từ db_location
# def get_place_gdf():
#     geometry = [Point(float(i['coordinate'][0]),float(i['coordinate'][1])) for i in ggres]
#     d = {'name_list': name_list,
#         'geometry': geometry}
#     gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
#     return gdf

# ### Tạo GeoDataFrame từ db_fnb
# def get_fnb_gdf():
#     geometry = [Point(float(i['coordinate'][0]),float(i['coordinate'][1])) for i in ggres]
#     d = {'name_list': name_list,
#         'geometry': geometry}
#     gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
#     return gdf



@app.route('/ind-loc', methods = ['POST'])
def get_ind_loc():
    data = request.get_json()
    print("", data)

    mongo_results = []
    query = {}
    if data["is_interests"]:
        query["interests"] = {"$all": data["interests_select"]}

    if data["is_moods"]:
        query["moods"] = {"$all": data["moods_select"]}

    names_res, img_res, coor_res, ggmap_res, interests_res, moods_res = [], [], [], [], [], []

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

    return jsonify({'names_res':names_res, 'img_res': img_res, 'coor_res': coor_res, 'ggmap_res':ggmap_res, 'interests_res': interests_res, 'moods_res': moods_res})

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

    names_res, img_res, coor_res, ggmap_res, interests_res, moods_res = [], [], [], [], [], []
    mongo_results = list(collection.find(query))
    print(mongo_results)
    for index, result in enumerate(mongo_results, start=1):
            result["order"] = index
            names_res.append(result["name"])
            img_res.append(result["img_url"])
            coor_res.append(result["coordinate"])
            ggmap_res.append(result["gg_map"])
            interests_res.append(result["interests"])
            moods_res.append(result["moods"])

    
    
    return jsonify({'names_res':names_res, 'img_res': img_res, 'coor_res': coor_res, 'ggmap_res':ggmap_res, 'interests_res': interests_res, 'moods_res': moods_res})


@app.route('/bruh', methods = ['GET'])
def asda():
    return "bruh"

# @app.route('/find-route', methods = ['POST'])
# def find_route():
#     data = request.get_json()
#     origin_node = data["origin_node"]
#     destination_node = data["destination_node"]
#     route_nodes = ox.routing.shortest_path(G, origin_node, destination_node, weight="length")
#     points_list = [[G.nodes[node]['y'],G.nodes[node]['x']] for node in route_nodes]
#     return points_list

if __name__ == "__main__":
    app.run(debug= True)