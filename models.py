from init import db


class Sector(db.Model):
    __tablename__ = "sectors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)

    riders = db.relationship("Rider", backref="sector", lazy=True)


class Rider(db.Model):
    __tablename__ = "riders"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    number = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(16))

    sector_id = db.Column(db.Integer, db.ForeignKey("sectors.id"), nullable=True)

    results = db.relationship("Result", backref="rider", lazy=True)
    gear = db.relationship("Gear", backref="rider", lazy=True)
    trainings = db.relationship("Training", backref="rider", lazy=True)

    def __repr__(self):
        return "Rider({}; {}; {})".format(self.first_name, self.last_name, self.number)


class Result(db.Model):
    __tablename__ = "results"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Interval)
    time_seconds = db.Column(db.Integer)
    distance = db.Column(db.Float)
    category = db.Column(db.String(16))

    place_open = db.Column(db.Integer)
    riders_open = db.Column(db.Integer)
    place_category = db.Column(db.Integer)
    riders_category = db.Column(db.Integer)

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


class Team(db.Model):
    __tablename__ = "team"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    established = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(64), nullable=False)


class Gear(db.Model):
    __tablename__ = "gear"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    type = db.Column(db.String(32), nullable=False)

    rider_id = db.Column(db.Integer, db.ForeignKey("riders.id"), nullable=False)


class Training(db.Model):
    __tablename__ = "trainings"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), nullable=False)
    distance = db.Column(db.Float)
    time = db.Column(db.Interval)
    average_speed = db.Column(db.Float)
    elevation = db.Column(db.Integer)
    
    rider_id = db.Column(db.Integer, db.ForeignKey("riders.id"), nullable=False)
    