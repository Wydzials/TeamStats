from flask import render_template, redirect, url_for, request, session
from sqlalchemy import func
from models import Rider, Result, Event, Team, Gear, Training, Sector

from dotenv import load_dotenv, find_dotenv
import pandas as pd
import os

import imports
from init import db, app

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
    rider = Rider.query.get(rider_id)
    gear = Gear.query.filter_by(rider_id=rider_id).all()

    results = Result.query.filter_by(rider_id=rider.id).all()
    sorted_results = sorted(results, key=lambda k: k.event.date, reverse=True)

    trainings = Training.query.filter_by(rider_id=rider.id).order_by(Training.date.desc()).limit(20).all()

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
                           trainings=trainings)


@app.route("/event/<int:event_id>")
def event(event_id):
    event = Event.query.get(event_id)
    results = Result.query.filter_by(event_id=event_id).all()
    return render_template("event.html", event=event, results=results)


@app.route("/sectors")
def sectors():
    sectors = Sector.query.all()
    riders_by_sector = {}

    for sector in sectors:
        riders = Rider.query.filter_by(sector_id=sector.id).all()
        if len(riders) > 0:
            riders_by_sector[sector.name] = riders

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


@app.route("/result/add", methods=["GET", "POST"])
def add_result():
    if is_admin():
        if request.method == "GET":
            riders = Rider.query.all()
            events = Event.query.order_by(Event.date.desc()).all()
            return render_template("add_result.html", riders=riders, events=events)
        else:
            hours = request.form["hours"]
            minutes = request.form["minutes"]
            seconds = request.form["seconds"]

            time = pd.to_timedelta(f"{hours}:{minutes}:{seconds}")
            time_seconds = time.total_seconds()

            p_open = request.form["place-open"]
            p_category = request.form["place-category"]

            place_open = int(p_open.split('/')[0])
            riders_open = int(p_open.split('/')[1])

            place_category = int(p_category.split('/')[0])
            riders_category = int(p_category.split('/')[1])

            new_result = Result(time=time,
                                time_seconds=time_seconds,
                                rider_id=request.form["rider"],
                                event_id=request.form["event"],
                                distance=request.form["distance"],
                                category=request.form["category"],
                                place_open=place_open,
                                riders_open=riders_open,
                                place_category=place_category,
                                riders_category=riders_category)
            db.session.add(new_result)
            db.session.commit()
            return redirect(url_for("index"))
    return no_access()


@app.route("/result/delete/<int:id>")
def delete_result(id):
    if is_admin():
        Result.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(redirect_url())
    else:
        return no_access()


@app.route("/events")
def events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template("events.html", events=events)


@app.route("/event/add", methods=["GET", "POST"])
def add_event():
    if request.method == "GET":
        return render_template("add_event.html")
    else:
        if is_admin():
            date = pd.to_datetime(request.form["date"])
            new_event = Event(name=request.form["name"], date=date)
            db.session.add(new_event)
            db.session.commit()
            return redirect(url_for("index"))
        else:
            return no_access()


@app.route("/event/delete/<int:id>")
def delete_event(id):
    if is_admin():
        Event.query.filter_by(id=id).delete()
        Result.query.filter_by(event_id=id).delete()
        db.session.commit()
        return redirect(redirect_url())
    else:
        return no_access()


@app.route("/rider/<int:id>/edit", methods=["GET", "POST"])
def edit_rider(id):
    if is_admin():
        if request.method == "GET":
            rider = Rider.query.get(id)
            sectors = Sector.query.all()
            return render_template("edit_rider.html", rider=rider, sectors=sectors)
        else:
            rider = Rider.query.get(id)

            rider.first_name = request.form["first-name"]
            rider.last_name = request.form["last-name"]
            rider.number = int(request.form["number"])
            rider.category = request.form["category"]
            rider.sector_id = request.form["sector-id"]

            db.session.commit()
            return redirect(url_for("index"))
    else:
        return no_access()


def is_admin():
    return "username" in session and session["username"] == "admin"


def no_access():
    return "Brak dostępu!", 401


def redirect_url():
    return request.args.get("next") or request.referrer or url_for("index")


if __name__ == "__main__":
    # imports.import_all()
    app.run(debug=True)
