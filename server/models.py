from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="activity")
    campers = association_proxy("signups", "camper")
    # Add serialization rules
    serialize_rules = ("-signups.activity",)

    def __repr__(self):
        return f"<Activity {self.id}: {self.name}>"


class Camper(db.Model, SerializerMixin):
    __tablename__ = "campers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="camper")
    activities = association_proxy("signups", "activity")
    # Add serialization rules
    serialize_rules = ("-signups.camper",)

    # Add validation
    @validates("name")
    def validates_name(self, key, new_name):
        if not new_name:
            raise ValueError("validation errors")
        return new_name

    @validates("age")
    def validates_age(self, key, new_age):
        if not new_age or new_age < 8 or new_age > 18:
            raise ValueError("validation errors")
        return new_age

    def __repr__(self):
        return f"<Camper {self.id}: {self.name}>"


class Signup(db.Model, SerializerMixin):
    __tablename__ = "signups"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)

    # Add relationships
    camper = db.relationship("Camper", back_populates="signups")
    activity = db.relationship("Activity", back_populates="signups")
    # Add serialization rules
    serialize_rules = (
        "-camper.signups",
        "-activity.signups",
    )

    # Add validation
    @validates("time")
    def validates_time(self, key, new_time):
        if new_time < 0 or new_time > 23:
            raise ValueError("validation errors")
        return new_time

    def __repr__(self):
        return f"<Signup {self.id}>"


# add any models you may need.
