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
    __tablename__ = "sector"
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
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.sector_id"), nullable = False)

"""
CREATE TABLE "org_resource" (
	"org_id"	INTEGER NOT NULL,
	"resource_id"	INTEGER NOT NULL,
	FOREIGN KEY("org_id") REFERENCES "organization"("org_id"),
	FOREIGN KEY("resource_id") REFERENCES "resources"("resource_id"),
	PRIMARY KEY("org_id","resource_id")
)
"""
class OrgResource(db.Model):
    __tablename__ = "org_resource"
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"), primary_key = True, nullable = False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.resource_id"), primary_key = True, nullable = False)

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
    sector_list = Sector.query.all()
    return render_template(
        "view_sector.html",
        sector_list = sector_list
    )

@app.route("/sector/create", methods = ["GET", "POST"])
def create_sector():
    if request.method == "GET":
        return render_template("create_sector.html")
    elif request.method == "POST":
        sector_name = request.form.get("sector_name")

        data = Sector(
            sector_name = sector_name
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Sector"
            )
        else:
            db.session.commit()
            return redirect("/sector")

@app.route("/sector/<int:sector_id>/update", methods = ["GET", "POST"])
def update_sector(sector_id):
    try:
        sector_id = int(sector_id)
        old_data = Sector.query.get(sector_id)

        if request.method == "GET":
            return render_template(
                "update_sector.html",
                sector_id = sector_id,
                sector_name = old_data.sector_name
            )
        elif request.method == "POST":
            u_sector_name = request.form.get("sector_name")

            # Update data
            old_data.sector_name = u_sector_name

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
        return redirect("/sector")

@app.route("/sector/<int:sector_id>/delete", methods = ["GET", "POST"])
def delete_sector(sector_id):
    try:
        sector_id = int(sector_id)
        data = Sector.query.get(sector_id)
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/sector")

    except:
        return render_template(
            "error.html"
        )

@app.route("/organization", methods = ["GET", "POST"])
def view_organization():
    org_list = Organizations.query.all()
    org_data = []
    for org in org_list:
        data = {
            "org_id": org["org_id"],
            "org_name": org["org_name"],
            "state": State.query.get(org["state_id"]),
            "sector": Sector.query.get(org["sector_id"])
        }
        org_data.append(data)


    return render_template(
        "view_organization.html",
        org_data = org_data
    )

@app.route("/organization/create", methods = ["GET", "POST"])
def create_organization():
    if request.method == "GET":
        state_list = State.query.all()
        sector_list = Sector.query.all()
        return render_template(
            "create_organization.html",
            state_list = state_list,
            sector_list = sector_list
        )
    elif request.method == "POST":
        org_name = request.form.get("org_name")
        state_id = request.form.get("state_select")
        sector_id = request.form.get("sector_select")

        data = Organizations(
            org_name = org_name,
            state_id = state_id,
            sector_id = sector_id
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Organization"
            )
        else:
            db.session.commit()
            return redirect("/organization")


@app.route("/organization/<int:org_id>/update", methods = ["GET", "POST"])
def update_sector(org_id):
    try:
        org_id = int(org_id)
        old_data = Organizations.query.get(org_id)
        state_list = State.query.all()
        sector_list = Sector.query.all()

        if request.method == "GET":
            return render_template(
                "update_organization.html",
                org_id = org_id,
                org_name = old_data.org_name,
                state_list = state_list,
                sector_list = sector_list,
                state_id = old_data.state_id,
                sector_id = old_data.sector_id
            )
        elif request.method == "POST":
            u_org_name = request.form.get("org_name")
            u_state_id = request.form.get("state_select")
            u_sector_id = request.form.get("sector_select")

            # Update data
            old_data.org_name = u_org_name
            old_data.state_id = u_state_id
            old_data.sector_id = u_sector_id

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
        return redirect("/organization")

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=True
    )