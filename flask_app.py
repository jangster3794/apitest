from flask import Flask, render_template, request, Response
import csv
import psycopg2
import json
from math import sin, cos, sqrt, atan2, radians

conn_string = "dbname=mydb user=postgres password=12345678"
conn = psycopg2.connect(conn_string)
cursor=conn.cursor()

conn_string_geo = "dbname=geojsondb user=postgres password=12345678"
conn_geo = psycopg2.connect(conn_string_geo)
cursor_geo=conn_geo.cursor()

app= Flask(__name__)

@app.route("/")
def index():
    if request.method == "GET":
        select_statement = ("Select * from data.temp_table")
        cursor.execute(select_statement)
        rows  = cursor.fetchall()
        return render_template ('new.html', rows=rows)

@app.route("/post_location", methods=["GET","POST"])
def add_data():
    if request.method =='POST':
        key         = request.form['key']
        place_name  = request.form['place_name']
        admin_name1 = request.form['admin_name1']
        latitude    = request.form['latitude']
        longitude   = request.form['longitude']
        accuracy    = request.form['accuracy']
        data = (key,place_name,admin_name1,latitude,longitude,accuracy)
        insert_statement = "INSERT INTO data.temp_table (key,place_name,admin_name1,latitude,longitude,accuracy)""VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_statement, data )
        conn.commit()
    return render_template('add-form.html')

@app.route("/get_using_postgres")
def in_radius_postgres():
    return 'Coming soon.'

@app.route("/get_using_self", methods=["GET", "POST"])
def in_radius():
    if request.method=='GET':
        return render_template ('get-distance.html')
    if request.method=='POST':
        select_statement = ("Select * from data.temp_table")
        cursor.execute(select_statement)
        rows  = cursor.fetchall()
        lat1 = float(request.form['latitude'])
        lon1 = float((request.form['longitude']))
        distance_asked=float(request.form['distance'])
        avail_pincodes=[]
        for row in rows:
            if not row[3] or not row[4]:
                continue
            lat2 = float (row[3])
            lon2 = float (row[4])
            R = 6373.0
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c/62.137
            if distance<distance_asked:
                avail_pincodes.append(row)
        return render_template('result.html', rows=avail_pincodes)

@app.route('/geo_json', methods=["GET", "POST"])

# Functions used to add json to database
# def format_data(json_data):
#     data = []
#     for each in json_data["features"]:
#         for coord in each["geometry"]["coordinates"][0]:
#             data.append({"name":each["properties"]["name"], "type":each["properties"]["type"], "parent":each["properties"]["parent"], "geo_type":each["geometry"]["type"], "lat":coord[0], "lon":coord[1]})
#     return data

# def call_json():
#     with open(r"C:\Users\Tashu.JANGSTER\Desktop\Interview\geojson.json", "r") as f:
#         json_data = json.loads(f.read())
#         all_data = format_data(json_data)
#         insert_statement = """INSERT INTO geojson.data (name,type,parent,geo_type,geo_lat,geo_lon) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"""
        
#         for data in all_data:
#             name=data['name']
#             itype=data['type']
#             parent=data['parent']
#             geo_type=data['geo_type']
#             geo_lat=data['lat']
#             geo_lon=data['lon']
#             cursor_geo.execute(insert_statement % (name,itype,parent,geo_type,geo_lat,geo_lon))
#             conn_geo.commit()

def geo_json():
    if request.method=='GET':
        return render_template('get-geo-json.html')

    if request.method=='POST':
        lat = float (request.form['geo_lat'])
        lon = float (request.form['geo_lon'])
        select_statement = ("Select * from geojson.data")
        cursor_geo.execute(select_statement)
        rows  = cursor_geo.fetchall()
        all_coords=[]
        for row in rows:
            if lat==float (row[4]) and lon==float(row[5]):
                all_coords.append(row)
                print (row)
        return render_template('result-geo-json.html',rows=all_coords)

if __name__ == "__main__":
    app.run(debug=True)