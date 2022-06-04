from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/landing-page')
def landingpage():
    return render_template("landing-page.html")

if __name__ == "__main__":
    app.run(debug=True)