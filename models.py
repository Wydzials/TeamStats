from init import db


class Rider(db.Model):
    __tablename__ = "riders"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(16))
    sector = db.Column(db.Integer)

    results = db.relationship("Result", backref="rider", lazy=True)

    def __repr__(self):
        return "Rider({}; {}; {})".format(self.first_name, self.last_name, self.number)


class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Interval)
    time_seconds = db.Column(db.Integer)
    length = db.Column(db.Float)
    category = db.Column(db.String(16))
    rider_id = db.Column(db.Integer, db.ForeignKey("riders.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    def __repr__(self):
        return "Result({}; {}; {})".format(self.time, self.rider_id, self.event_id)


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime(), nullable=False)
    city = db.Column(db.String(64), nullable=True)

    results = db.relationship("Result", backref="event", lazy=True)

    def __repr__(self):
        return "Event({}; {}; {})".format(self.name, self.date, self.city)
