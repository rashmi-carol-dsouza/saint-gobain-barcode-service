import os
from dataclasses import dataclass

from flask import Flask, render_template, request, redirect, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@dataclass
class Barcode(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True))
    production_line = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __repr__(self):
        return '<Barcode %r' % self.id


@app.route('/')
def index():
    return render_template("index.html")


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

@app.route('/barcodes', methods=["POST", "GET"])
def barcode():
    if request.method == "POST":
        scanned_barcode = request.form["barcode"]
        production_line = request.form["productionLine"]
        new_scan = Barcode(id=scanned_barcode, production_line=production_line)
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
