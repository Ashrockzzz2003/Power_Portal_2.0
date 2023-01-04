from flask import Flask, redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os

# Get Directory for db
current_dir = os.path.abspath(os.path.dirname(__file__))

# Config
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(
    current_dir, "database.db"
)
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


"""
CREATE TABLE "states" (
	"state_id"	INTEGER NOT NULL UNIQUE,
	"state_name"	TEXT NOT NULL UNIQUE,
	"gdp_state_percapita"	REAL NOT NULL,
	PRIMARY KEY("state_id" AUTOINCREMENT)
)
"""
class State(db.Model):
    __tablename__ = "states"
    state_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
    state_name = db.Column(db.String, nullable = False, unique = True)
    gdp_state_percapita = db.Column(db.Float)


"""
CREATE TABLE "resources" (
	"resource_id"	INTEGER NOT NULL UNIQUE,
	"resource_type"	TEXT NOT NULL UNIQUE,
	"resource_left"	REAL NOT NULL,
	PRIMARY KEY("resource_id" AUTOINCREMENT)
)
"""
class Resource(db.Model):
    __tablename__ = "resources"
    resource_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
    resource_type = db.Column(db.String, nullable = False, unique = True)
    resource_left = db.Column(db.Float, nullable = False)

"""
CREATE TABLE "sector" (
	"sector_id"	INTEGER NOT NULL UNIQUE,
	"sector_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("sector_id" AUTOINCREMENT)
)
"""
class Sector(db.Model):
    __tablename__ = "sectors"
    sector_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
    sector_name = db.Column(db.String, nullable = False, unique = True)

"""
CREATE TABLE "organization" (
	"org_id"	INTEGER NOT NULL UNIQUE,
	"org_name"	TEXT NOT NULL UNIQUE,
	"state_id"	INTEGER NOT NULL,
	FOREIGN KEY("state_id") REFERENCES "states"("state_id"),
	PRIMARY KEY("org_id" AUTOINCREMENT)
)
"""
class Organizations(db.Model):
    __tablename__ = "organizations"
    org_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
    org_name = db.Column(db.String, nullable = False, unique = True)
    state_id = db.Column(db.Integer, db.ForeignKey("states.state_id"), nullable = False)
    sector_id = db.Column(db.integer, db.ForeignKey("sector.sector_id"), nullable = False)

@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template(
        "index.html"
    )

@app.route("/state", methods = ["GET"])
def view_state():
    state_list = State.query.all()
    return render_template(
        "view_state.html",
        state_list = state_list
    )

@app.route("/state/create", methods = ["GET", "POST"])
def create_state():
    if request.method == "GET":
        return render_template("create_state.html")
    elif request.method == "POST":
        state_name = request.form.get("state_name")
        gdp_state_percapita = request.form.get("gdp_state_percapita")

        data = State(
            state_name = state_name,
            gdp_state_percapita = gdp_state_percapita
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "State"
            )
        else:
            db.session.commit()
            return redirect("/state")

@app.route("/state/<int:state_id>/update", methods = ["GET", "POST"])
def update_state(state_id):
    try:
        state_id = int(state_id)
        old_data = State.query.get(state_id)

        if request.method == "GET":
            return render_template(
                "update_state.html",
                state_id = state_id,
                state_name = old_data.state_name,
                gdp_state_percapita = old_data.gdp_state_percapita
            )
        elif request.method == "POST":
            u_state_name = request.form.get("state_name")
            u_gdp_state_percapita = request.form.get("gdp_state_percapita")

            # Update data
            old_data.state_name = u_state_name
            old_data.gdp_state_percapita = u_gdp_state_percapita

            try:
                db.session.add(old_data)
            except:
                db.session.rollback()
                return render_template(
                    "error.html"
                )
            else:
                db.session.commit()
    except:
        return render_template(
            "error.html"
        )
    else:
        return redirect("/state")

# Pending
@app.route("/state/<int:state_id>/delete")
def delete_student(state_id):
    try:
        state_id = int(state_id)
        data = State.query.get(state_id)
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/state")


    except:
        return render_template(
            "error.html"
        )

@app.route("/resource")
def view_resource():
    resource_list = Resource.query.all()
    return render_template(
        "view_resource.html",
        resource_list = resource_list
    )

@app.route("/resource/create", methods = ["GET", "POST"])
def create_resource():
    if request.method == "GET":
        return render_template("create_resource.html")
    elif request.method == "POST":
        resource_type = request.form.get("resource_type")
        resource_left = request.form.get("resource_left")

        data = Resource(
            resource_type = resource_type,
            resource_left = resource_left
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Resource"
            )
        else:
            db.session.commit()
            return redirect("/resource")

@app.route("/resource/<int:resource_id>/update", methods = ["GET", "POST"])
def update_resource(resource_id):
    try:
        resource_id = int(resource_id)
        old_data = Resource.query.get(resource_id)

        if request.method == "GET":
            return render_template(
                "update_resource.html",
                resource_id = resource_id,
                resource_type = old_data.resource_type,
                resource_left = old_data.resource_left
            )
        elif request.method == "POST":
            u_resource_type = request.form.get("resource_type")
            u_resource_left = request.form.get("resource_left")

            # Update data
            old_data.resource_type = u_resource_type
            old_data.resource_left = u_resource_left

            try:
                db.session.add(old_data)
            except:
                db.session.rollback()
                return render_template(
                    "error.html"
                )
            else:
                db.session.commit()
    except:
        return render_template(
            "error.html"
        )
    else:
        return redirect("/resource")


# Pending
@app.route("/resource/<int:resource_id>/delete")
def delete_resource(resource_id):
    try:
        resource_id = int(resource_id)
        data = Resource.query.get(resource_id)
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/resource")


    except:
        return render_template(
            "error.html"
        )

@app.route("/sector", methods = ["GET", "POST"])
def view_sector():
    
    return

@app.route("/organization", methods = ["GET", "POST"])
def view_organization():
    org_list = Organizations.query.all()
    return render_template(
        "view_org.html",
        org_list = org_list
    )


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True
    )