#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return "Homepage"


@app.route("/campers", methods=["GET", "POST"])
def campers():
    if request.method == "GET":
        return make_response(
            [
                camper.to_dict(only=("id", "name", "age"))
                for camper in Camper.query.all()
            ],
            200,
        )

    elif request.method == "POST":
        data = request.json
        try:
            camper = Camper(name=data["name"], age=data["age"])
            db.session.add(camper)
            db.session.commit()
            return make_response(camper.to_dict(), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)


@app.route("/campers/<int:id>", methods=["GET", "PATCH", "DELETE"])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        if request.method == "GET":
            return make_response(camper.to_dict(), 200)

        elif request.method == "PATCH":
            try:
                data = request.json
                for attr in data:
                    setattr(camper, attr, data[attr])
                    db.session.commit()
                return make_response(camper.to_dict(), 202)
            except Exception as e:
                return make_response({"errors": [str(e)]}, 400)
    else:
        return make_response({"error": "Camper not found"}, 404)


@app.route("/activities")
def activities():
    return make_response(
        [
            activity.to_dict(only=("id", "name", "difficulty"))
            for activity in Activity.query.all()
        ],
        200,
    )


@app.route("/activities/<int:id>", methods=["GET", "DELETE"])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        if request.method == "GET":
            return make_response(activity.to_dict(), 200)

        elif request.method == "DELETE":
            for signup in activity.signups:
                db.session.delete(signup)
                db.session.commit()
            db.session.delete(activity)
            db.session.commit
            return make_response("", 204)
    else:
        return make_response({"error": "Activity not found"}, 404)


@app.route("/signups", methods=["GET", "POST"])
def signups():
    if request.method == "GET":
        return make_response(
            [signup.to_dict() for signup in Signup.query.all()],
            200,
        )

    elif request.method == "POST":
        data = request.json
        try:
            signup = Signup(
                camper_id=data["camper_id"],
                activity_id=data["activity_id"],
                time=data["time"],
            )
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(), 201)
        except Exception as e:
            return make_response({"errors": [str(e)]}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
