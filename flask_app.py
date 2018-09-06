from flask import Flask, render_template, request, Response
import csv
import psycopg2
from math import sin, cos, sqrt, atan2, radians

conn_string = "dbname=mydb user=postgres password=12345678"
conn = psycopg2.connect(conn_string)
cursor=conn.cursor()

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

@app.route('/get_using_self', methods=["GET", "POST"])
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
                print(row)
                continue
            lat2 = float (row[3])
            lon2 = float (row[4])
            R = 6373.0
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            if distance<distance_asked:
                avail_pincodes.append(row)
        return render_template('result.html', rows=avail_pincodes)
        
if __name__ == "__main__":
    app.run(debug=True)