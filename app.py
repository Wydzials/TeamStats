from flask import render_template

import imports
from init import db, app
from sqlalchemy import func
from models import Rider, Result, Event, Team, Gear, Training


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
    distance_sum = db.session.query(func.sum(Result.distance)).filter_by(rider_id=rider.id).scalar()
    time_seconds = db.session.query(func.sum(Result.time_seconds)).filter_by(rider_id=rider.id).scalar()
    time_sum = round(time_seconds / 3600, 1)
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


if __name__ == "__main__":
    imports.import_all()
    app.run(debug=True)
