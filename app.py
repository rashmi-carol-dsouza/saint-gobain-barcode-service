from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Barcode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r' % self.id


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/landing_page')
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
        new_scan = Barcode(barcode=scanned_barcode)
        try:
            db.session.add(new_scan)
            db.session.commit()
            return redirect("/")
        except:
            return "There was an issue adding the code"
    else:
        return render_template("barcode.html")


if __name__ == "__main__":
    app.run(debug=True)
