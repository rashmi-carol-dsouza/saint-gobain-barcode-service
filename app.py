import csv
import io
import os
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy
from flask import Flask, render_template, request, redirect, make_response, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, DATETIME
from sqlalchemy.connectors import pyodbc
from sqlalchemy.dialects.postgresql import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@dataclass
class Barcode(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    production_line = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return '<Barcode %r' % self.id


@app.route('/')
def index():
    return render_template("loginsg.html")


@app.route('/landing_page', methods=["POST", "GET"])
def landing_page():
    return render_template("landing_page.html")



@app.route('/view_scans', methods=["GET"])
def view_scans():
    all_barcodes = Barcode.query.order_by(Barcode.date_created).all()
    return render_template("view_scans.html", barcodes=all_barcodes)


@app.route('/scan', methods=["POST", "GET"])
def scan():
    if request.method == "POST":
        scanned_barcode = request.form["barcode"]
        production_line = request.form["productionLine"]
        new_scan = Barcode(id=scanned_barcode, production_line=production_line,date_created=db.func.current_timestamp())
        try:
            db.session.add(new_scan)
            db.session.commit()
            return make_response(jsonify([{'msg': "success"}]), 201)
            return redirect("/")
        except Exception as inst:
            print(inst)
            return "There was an issue adding the code"
    else:
        return render_template("barcode.html")
#
# @app.route("/download")
# def download_file():
#     with open(r'C:\Users\Rashmi Dsouza\PycharmProjects\product.csv', 'w') as s_key:
#         p = db.query.all()
#         for i in p:
#             # x16 = tuple(x15)
#             csv_out = csv.writer(s_key)
#             csv_out.writerow(p)
#     return send_file(p, as_attachment=True)


@app.route("/download_csv")
def download_csv():
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect("host=localhost dbname=db user=u password=p")

        cursor = conn.cursor()

        cursor.execute('SELECT id FROM table')
        conn.commit()
        result = cursor.fetchall()
        #fetchone()

        output = io.StringIO()
        writer = csv.writer(output)

        line = ['column1,column2']
        writer.writerow(line)

        for row in result:
            line = [row[0] + ' , ' + row[1] + ' , ']
            writer.writerow(line)

        output.seek(0)

        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=report.csv"})
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



@app.route('/barcodes', methods=["POST", "GET"])
def barcode():
    if request.method == "POST":
        scanned_barcode = request.form["barcode"]
        production_line = request.form["productionLine"]
        new_scan = Barcode(id=scanned_barcode, production_line=production_line,date_created=db.func.current_timestamp())
        try:
            db.session.add(new_scan)
            db.session.commit()
            last_added_barcode = Barcode.query.get(scanned_barcode)
            return make_response(jsonify(last_added_barcode.to_dict()), 201)
        except Exception as inst:
            print(inst)
            return "There was an issue adding the code"
    else:
        all_barcodes = Barcode.query.all()
        barcodes = []
        for barcode in all_barcodes:
            barcodes.append(barcode.to_dict())
        return jsonify(barcodes)

if __name__ == "__main__":
    app.run(debug=True)
