import csv
from init import db, app
from models import Rider, Event, Result
import pandas as pd


def import_riders():
    print("Importing riders...")
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


def import_events():
    with open("data/events.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date = pd.to_datetime(row["date"])
            new_event = Event(name=row["name"],
                              date=date,
                              city=row["city"])
            if Event.query.filter_by(date=new_event.date).first() is None:
                db.session().add(new_event)
        db.session.commit()


def new_import():
    with open("data/results.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                time = pd.to_timedelta(row["time"])
                time_seconds = time.total_seconds()
                date = pd.to_datetime(row["date"])
                names = row["rider"].split()
                rider_id = Rider.query.filter_by(first_name=names[0], last_name=names[1]).first().id
                name = row["name"]

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
                                            length=row["length"],
                                            category=row["category"])
                        db.session.add(new_result)

            except:
                print("Invalid row number " + str(reader.line_num))

        db.session.commit()
