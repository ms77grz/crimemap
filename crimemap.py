import datetime
import dateparser
import dbconfig
if dbconfig.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper
from flask import Flask, render_template, request, redirect, url_for, flash
import json
import string


app = Flask(__name__)
app.secret_key = dbconfig.secret_key
DB = DBHelper()
categories = ['mugging', 'break-in', 'robbery', 'burglary']


def format_date(userdate):
    date = dateparser.parse(userdate)
    try:
        return datetime.datetime.strftime(date, "%Y-%m-%d")
    except TypeError:
        return None


def sanitize_string(userinput):
    whitelist = string.ascii_letters + string.digits + " !?$.,;:-'()&"
    return ''.join(list(filter(lambda x: x in whitelist, userinput)))


@app.route("/")
def home():
    crimes = DB.get_all_crimes()
    crimes = json.dumps(crimes)
    return render_template("home.html", crimes=crimes, categories=categories)


@app.route("/submitcrime", methods=["POST"])
def submitcrime():
    category = request.form.get("category")
    if category not in categories:
        return redirect(url_for("home"))
    date = format_date(request.form.get("date"))
    if not date:
        flash("Invalid date. Please use yyyy-mm-dd format")
        return redirect(url_for("home"))
    try:
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
    except ValueError:
        return redirect(url_for("home"))
    description = sanitize_string(request.form.get("description"))
    DB.add_crime(category, date, latitude, longitude, description)
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
