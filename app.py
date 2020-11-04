from flask import render_template, redirect, url_for, request, session

import imports
from init import db, app
from sqlalchemy import func
from models import Rider, Result, Event, Team, Gear, Training, Sector

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return team()


@app.route("/team", methods=["POST", "GET"])
def team():
    riders = Rider.query.all()
    team = Team.query.first()

    results_count = db.session.query(Result).count()
    distance_sum = db.session.query(func.sum(Result.distance)).scalar()
    time_seconds = db.session.query(func.sum(Result.time_seconds)).scalar()
    time_sum = round(time_seconds / 3600, 1)

    stats = {"results_count": results_count,
             "distance_sum": distance_sum,
             "time_sum": time_sum}

    return render_template("team.html", riders=riders, team=team, stats=stats)


@app.route("/rider/<int:rider_id>")
def rider(rider_id):
    rider = Rider.query.filter_by(id=rider_id).first()
    gear = Gear.query.filter_by(rider_id=rider_id).all()

    results = Result.query.filter_by(rider_id=rider.id).all()
    sorted_results = sorted(results, key=lambda k: k.event.date, reverse=True)

    trainings = Training.query.filter_by(rider_id=rider.id).all()
    sorted_trainings = sorted(trainings, key=lambda k: k.date, reverse=True)[:20]

    results_count = db.session.query(Result).filter_by(rider_id=rider.id).count()
    distance_sum = db.session.query(func.sum(Result.distance)).filter_by(rider_id=rider.id).scalar() or 0
    time_seconds = db.session.query(func.sum(Result.time_seconds)).filter_by(rider_id=rider.id).scalar() or 0
    time_sum = round(time_seconds / 3600, 1)

    avg_speed = 0
    if time_seconds != 0:
        avg_speed = round(distance_sum / (time_seconds / 3600), 1)

    stats = {"results_count": results_count,
             "distance_sum": distance_sum,
             "time_sum": time_sum,
             "avg_speed": avg_speed}

    return render_template("rider.html",
                           rider=rider,
                           stats=stats,
                           gear=gear,
                           results=sorted_results,
                           trainings=sorted_trainings)


@app.route("/event/<int:event_id>")
def event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    results = Result.query.filter_by(event_id=event_id).all()
    return render_template("event.html", event=event, results=results)


@app.route("/last")
def last_event():
    events = Event.query.all()
    last_event = sorted(events, key=lambda k: k.date, reverse=True)[0]
    id = last_event.id
    return redirect(f"/event/{id}")


@app.route("/sectors")
def sectors():
    sectors = Sector.query.all()

    riders_by_sector = {}
    for sector in sectors:
        riders = Rider.query.filter_by(sector_id=sector.id).all()
        if len(riders) > 0:
            riders_by_sector[sector.name] = riders

    print(riders_by_sector)

    return render_template("sectors.html", sectors=sectors,
                           riders_by_sector=riders_by_sector)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Błędne dane logowania!")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


@app.route("/result/delete/<int:id>")
def delete_result(id):
    if "username" in session and session["username"] == "admin":
        Result.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(redirect_url())
    else:
        return "Brak dostępu!", 401


def redirect_url(default="index"):
    return request.args.get("next") or request.referrer or url_for(default)


if __name__ == "__main__":
    imports.import_all()
    app.run(debug=True)
