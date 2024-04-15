from flask import Flask, redirect, url_for, request, Response, render_template
from flask_mysqldb import MySQL
import json

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'solitarysrootpassword'
app.config['MYSQL_DB'] = 'eb_database'

mysql = MySQL(app)


@app.route('/')
def main_page():

    cursor = mysql.connection.cursor()
    cursor.execute("select movie_id, median_rating from ratings LIMIT 10;")
    data = cursor.fetchall()

    arr1 = []
    arr2 = []
    for i in range(len(data)):
        arr1.append(data[i][0])
        arr2.append(data[i][1])

    cursor.execute("select COUNT(movie_id), genre from genre group by genre;")
    data = cursor.fetchall()

    arr3 = []
    arr4 = []
    for i in range(len(data)):
        arr3.append(data[i][0])
        arr4.append(data[i][1])    

    cursor.close()

    print(arr3)
    print(arr4)

    return render_template("index.html", bar_x = json.dumps(arr1), bar_y = json.dumps(arr2),
                           pie_x = json.dumps(arr4), pie_y = json.dumps(arr3))


if __name__ == '__main__':
   app.run(host="0.0.0.0", port="8900", debug = True) 
