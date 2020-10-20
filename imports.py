import csv
from init import db
from models import Rider, Event, Result, Team, Gear, Training
import pandas as pd
import datetime


def import_team():
    with open("data/team.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            new_team = Team(name=row["name"],
                            established=row["established"],
                            city=row["city"])
            if Team.query.filter_by(name=new_team.name).first() is None:
                db.session.add(new_team)

        db.session.commit()


def import_riders():
    with open("data/riders.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if("#" in row["id"]):
                continue
            new_rider = Rider(id=row["id"],
                              first_name=row["first_name"],
                              last_name=row["last_name"],
                              number=row["number"],
                              sector=row["sector"],
                              category=row["category"])

            if Rider.query.filter_by(first_name=new_rider.first_name).filter_by(last_name=new_rider.last_name).first() is None:
                db.session.add(new_rider)
                print("Found new rider: {}".format(new_rider))
        db.session.commit()


def import_events_results():
    with open("data/results.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                time = pd.to_timedelta(row["time"])
                time_seconds = time.total_seconds()
                date = pd.to_datetime(row["date"])
                names = row["rider"].split()
                rider_id = Rider.query.filter_by(first_name=names[0].strip(), last_name=names[1].strip()).first().id
                name = row["name"]

                place_open = int(row["place_open"].split('/')[0])
                riders_open = int(row["place_open"].split('/')[1])

                place_category = int(row["place_category"].split('/')[0])
                riders_category = int(row["place_category"].split('/')[1])

                if pd.isnull(time):
                    raise Exception

                if Event.query.filter_by(name=name).filter_by(date=date).first() is None:
                    if len(name) > 0 and date is not None:
                        new_event = Event(name=name, date=date)
                        db.session.add(new_event)

                event_id = Event.query.filter_by(name=name).filter_by(date=date).first().id

                if Result.query.filter_by(event_id=event_id).filter_by(rider_id=rider_id).first() is None:
                    if rider_id is not None:
                        new_result = Result(time=time,
                                            time_seconds=time_seconds,
                                            rider_id=rider_id,
                                            event_id=event_id,
                                            distance=row["distance"],
                                            category=row["category"],
                                            place_open=place_open,
                                            riders_open=riders_open,
                                            place_category=place_category,
                                            riders_category=riders_category)
                        db.session.add(new_result)

            except:
                print("Invalid row number " + str(reader.line_num))

        db.session.commit()


def import_gear():
    with open("data/gear.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            names = row["rider"].split()
            rider_id = Rider.query.filter_by(first_name=names[0].strip(), last_name=names[1].strip()).first().id
            new_gear = Gear(name=row["name"],
                            rider_id=rider_id,
                            type=row["type"])

            if Gear.query.filter_by(rider_id=rider_id).filter_by(name=row["name"]).first() is None:
                db.session.add(new_gear)

        db.session.commit()


def import_trainings():
    with open("data/trainings.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = pd.to_datetime(row["date"])
            time = datetime.timedelta(seconds=int(row["moving_time"]))
            distance = float(row["distance"]) / 1000
            average_speed = distance / (time.seconds / 3600)

            names = row["rider"].split()
            rider_id = Rider.query.filter_by(first_name=names[0].strip(), last_name=names[1].strip()).first().id

            new_training = Training(rider_id=rider_id,
                                    date=date,
                                    time=time,
                                    distance=distance,
                                    average_speed=average_speed,
                                    elevation=round(float(row["elevation"])))

            if Training.query.filter_by(date=date).filter_by(distance=distance).first() is None:
                db.session.add(new_training)
            
        db.session.commit()


def import_all():
    import_team()
    import_riders()
    import_events_results()
    import_gear()
    import_trainings()
