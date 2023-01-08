from flask import Flask, redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import os
import random

# Get Directory for db
current_dir = os.path.abspath(os.path.dirname(__file__))

# Config
app = Flask(__name__, template_folder='templates')
"""
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
"""
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
    __tablename__ = "organization"
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

"""
CREATE TABLE "region" (
	"region_id"	INTEGER NOT NULL UNIQUE,
	"region_name"	TEXT NOT NULL UNIQUE,
	"death_count"	INTEGER NOT NULL,
	"allowed_pollution_level"	REAL NOT NULL,
	PRIMARY KEY("region_id" AUTOINCREMENT)
)
"""
class Region(db.Model):
    __tablename__ = "region"
    region_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True, autoincrement = True)
    region_name = db.Column(db.String, nullable = False, unique = True)
    death_count = db.Column(db.Integer, nullable = False)
    allowed_pollution_level = db.Column(db.Float, nullable = False)

"""
CREATE TABLE "plant" (
	"plant_id"	INTEGER NOT NULL UNIQUE,
	"plant_status"	TEXT NOT NULL CHECK("plant_status" IN ('ACTIVE', 'INACTIVE')),
	"spanned_area"	REAL NOT NULL,
	"production_cost"	REAL NOT NULL,
	"pollution_level"	REAL NOT NULL,
	"net_capacity"	REAL NOT NULL,
	"resource_id"	INTEGER NOT NULL,
	"org_id"	INTEGER NOT NULL,
	"region_id"	INTEGER NOT NULL,
	PRIMARY KEY("plant_id" AUTOINCREMENT),
	FOREIGN KEY("region_id") REFERENCES "region"("region_id"),
	FOREIGN KEY("org_id") REFERENCES "organization"("org_id"),
	FOREIGN KEY("resource_id") REFERENCES "resources"("resource_id")
)
"""
class Plants(db.Model):
    __tablename__ = "plant"
    plant_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
    plant_status = db.Column(db.String, nullable = False)
    spanned_area = db.Column(db.Float, nullable = False)
    production_cost = db.Column(db.Float, nullable = False)
    pollution_level = db.Column(db.Float, nullable = False)
    net_capacity = db.Column(db.Float, nullable = False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.resource_id"), nullable = False)
    region_id = db.Column(db.Integer, db.ForeignKey("region.region_id"), nullable = False)
    org_id = db.Column(db.Integer, db.ForeignKey("organization.org_id"), nullable = False)

"""
CREATE TABLE "daily_demand" (
	"date"	TEXT NOT NULL UNIQUE,
	"demand"	REAL NOT NULL,
	PRIMARY KEY("date")
)
"""
class DailyDemand(db.Model):
    __tablename__ = "daily_demand"
    date = db.Column(db.String, primary_key = True, nullable = False, unique = True)
    demand = db.Column(db.Float, nullable = False)

"""
CREATE TABLE "daily_reading" (
	"plant_id"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"energy_generated"	REAL NOT NULL,
	FOREIGN KEY("plant_id") REFERENCES "plant"("plant_id"),
	PRIMARY KEY("plant_id","date")
)
"""
class DailyReading(db.Model):
    __tablename__ = "daily_reading"
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.plant_id"), primary_key = True, nullable = False)
    date = db.Column(db.String, primary_key = True, nullable = False)
    energy_generated = db.Column(db.Float, nullable = False)


@app.route("/", methods = ["GET", "POST"])
def index():
    demand = db.session.execute("SELECT AVG(demand) FROM daily_demand").first()[0]
    supply = db.session.execute("SELECT AVG(energy_generated) FROM daily_reading").first()[0]

    source = [
        ["State_id", "State", "Capacity(MW)"],
        ['IN-AP', 'Andhra Pradesh'],
        ['IN-AR', 'Arunachal Pradesh'],
        ['IN-AS', 'Assam'],
        ['IN-BR', 'Bihar'],
        ['IN-CG', 'Chhattisgarh'],
        ['IN-GA', 'Goa'],
        ['IN-GJ', 'Gujarat'],
        ['IN-HR', 'Haryana'],
        ['IN-HP', 'Himachal Pradesh'],
        ['IN-JK', 'Jammu and Kashmir'],
        ['IN-JH', 'Jharkhand'],
        ['IN-KA', 'Karnataka'],
        ['IN-KL', 'Kerala'],
        ['IN-MP', 'Madhya Pradesh'],
        ['IN-MH', 'Maharashtra'],
        ['IN-MN', 'Manipur'],
        ['IN-ML', 'Meghalaya'],
        ['IN-MZ', 'Mizoram'],
        ['IN-NL', 'Nagaland'],
        ['IN-OD', 'Odisha'],
        ['IN-PB', 'Punjab'],
        ['IN-RJ', 'Rajasthan'],
        ['IN-SK', 'Sikkim'],
        ['IN-TN', 'Tamil Nadu'],
        ['IN-TS', 'Telangana'],
        ['IN-TR', 'Tripura'],
        ['IN-UK', 'Uttarakhand'],
        ['IN-UP', 'Uttar Pradesh'],
        ['IN-WB', 'West Bengal'],
        ['IN-AN', 'Andaman and Nicobar Islands'],
        ['IN-CH', 'Chandigarh'],
        ['IN-DN', 'Dadra and Nagar Haveli'],
        ['IN-DD', 'Daman and Diu'],
        ['IN-LD', 'Lakshadweep'],
        ['IN-DL', 'National Capital Territory of Delhi'],
        ['IN-PY', 'Puducherry']
    ]

    map_data = [["State_id", "State", "Sector", "Capacity(MW)"]]
    

    for i in range(1, len(source)):
        query = f"""
        SELECT state_name
        FROM states
        WHERE state_name = '{(source[i])[1]}'
        """
        exists = (db.session.execute(query).first())
        if(exists is not None):
            s_query = f"""
            SELECT SUM(dr.energy_generated)
            FROM daily_reading AS dr
            WHERE dr.plant_id IN (
                SELECT plant_id
                FROM plant
                WHERE org_id IN (
                    SELECT org_id
                    FROM organization
                    WHERE state_id IN (
                        SELECT state_id
                        FROM states
                        WHERE state_name = '{(source[i])[1]}'
                    )
                )
            )
            """
            se_data = (db.session.execute(s_query)).first()[0]

            if se_data is None:
                map_data.append([source[i][0], source[i][1], 0])
            else:
                map_data.append([source[i][0], source[i][1], se_data])
    
    resource_data = [["Type", "Capacity(MW)"]]

    resource_list = Resource.query.all()

    for resource in resource_list:
        query = f"""
        SELECT SUM(dr.energy_generated)
        FROM daily_reading AS dr
        WHERE dr.plant_id IN (
            SELECT plant_id
            FROM plant
            WHERE resource_id = {resource.resource_id}
        )
        """

        capacity = db.session.execute(query).first()[0]
        if(capacity is None):
            resource_data.append([resource.resource_type, 0])
        else:
            resource_data.append([resource.resource_type, capacity])
    
    hydro_data = []
    for i in range(1947, 2022):
        hydro_data.append([i, random.randint(1, 100)])
    thermal_data = []
    for i in range(1947, 2022):
        thermal_data.append([i, random.randint(1, 100)])
    nuclear_data = []
    for i in range(1947, 2022):
        nuclear_data.append([i, random.randint(11, 100)])

    return render_template(
        "index.html",
        source = map_data,
        resource_data = resource_data,
        hydro_data = hydro_data,
        thermal_data = thermal_data,
        nuclear_data = nuclear_data,
        demand = demand,
        supply = supply
    )

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(
            "login.html"
        )
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "nppadmin":
            return redirect("/state")
        else:
            return render_template(
                "login.html",
                alert = True
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

# Done
@app.route("/state/<int:state_id>/delete")
def delete_state(state_id):
    try:
        state_id = int(state_id)
        data = State.query.get(state_id)

        # Flush From Organization

        org_data = Organizations.query.all()

        for org in org_data:
            if org.state_id == state_id:
                try:
                    db.session.delete(org)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush from parent
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
        
        # Flush out From child

        plant_data = Plants.query.all()

        for plant in plant_data:
            if plant.resource_id == resource_id:
                try:
                    db.session.delete(plant)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush data from parent
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

        # Flush out from child

        org_data = Organizations.query.all()

        for org in org_data:
            if org.sector_id == sector_id:
                try:
                    db.session.delete(org)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush out from parent
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
            "org_id": org.org_id,
            "org_name": org.org_name,
            "state": State.query.get(org.state_id),
            "sector": Sector.query.get(org.sector_id)
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
def update_organization(org_id):
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

@app.route("/organization/<int:org_id>/delete", methods = ["GET", "POST"])
def delete_org(org_id):
    try:
        org_id = int(org_id)
        data = Organizations.query.get(org_id)

        # Flush from child

        plant_data = Plants.query.all()

        for plant in plant_data:
            if plant.org_id == org_id:
                try:
                    db.session.delete(plant)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush from parent
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/organization")

    except:
        return render_template(
            "error.html"
        )

@app.route("/region", methods = ["GET", "POST"])
def view_region():
    region_list = Region.query.all()
    return render_template(
        "view_region.html",
        region_list = region_list
    )

@app.route("/region/create", methods = ["GET", "POST"])
def create_region():
    if request.method == "GET":
        return render_template("create_region.html")
    elif request.method == "POST":
        region_name = request.form.get("region_name")
        death_count = request.form.get("death_count")
        allowed_pollution_level = request.form.get("allowed_pollution_level")

        data = Region(
            region_name = region_name,
            death_count = death_count,
            allowed_pollution_level = allowed_pollution_level
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Region"
            )
        else:
            db.session.commit()
            return redirect("/region")

@app.route("/region/<int:region_id>/update", methods = ["GET", "POST"])
def update_region(region_id):
    try:
        region_id = int(region_id)
        old_data = Region.query.get(region_id)

        if request.method == "GET":
            return render_template(
                "update_region.html",
                region_id = region_id,
                region_name = old_data.region_name,
                death_count = old_data.death_count,
                allowed_pollution_level = old_data.allowed_pollution_level
            )
        elif request.method == "POST":
            u_region_name = request.form.get("region_name")
            u_death_count = request.form.get("death_count")
            u_allowed_pollution_level = request.form.get("allowed_pollution_level")

            # Update data
            old_data.region_name = u_region_name
            old_data.death_count = u_death_count
            old_data.allowed_pollution_level = u_allowed_pollution_level

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
        return redirect("/region")

@app.route("/region/<int:region_id>/delete", methods = ["GET", "POST"])
def delete_region(region_id):
    try:
        region_id = int(region_id)
        data = Region.query.get(region_id)

        # Flush from child
        plant_data = Plants.query.all()

        for plant in plant_data:
            if plant.region_id == region_id:
                try:
                    db.session.delete(plant)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush from parent
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/region")

    except:
        return render_template(
            "error.html"
        )

@app.route("/plant", methods = ["GET", "POST"])
def view_plant():
    plant_list = Plants.query.all()
    plant_data = []
    for plant in plant_list:
        data = {
            "plant_id": plant.plant_id,
            "plant_status": plant.plant_status,
            "spanned_area": plant.spanned_area,
            "production_cost": plant.production_cost,
            "pollution_level": plant.pollution_level,
            "net_capacity": plant.net_capacity,
            "resource": Resource.query.get(plant.resource_id),
            "org": Organizations.query.get(plant.org_id),
            "region": Region.query.get(plant.region_id)
        }
        plant_data.append(data)


    return render_template(
        "view_plant.html",
        plant_data = plant_data
    )

@app.route("/plant/create", methods = ["GET", "POST"])
def create_plant():
    if request.method == "GET":
        resource_list = Resource.query.all()
        org_list = Organizations.query.all()
        region_list = Region.query.all()
        return render_template(
            "create_plant.html",
            resource_list = resource_list,
            org_list = org_list,
            region_list = region_list
        )
    elif request.method == "POST":
        plant_status = request.form.get("status_select")
        spanned_area = request.form.get("spanned_area")
        production_cost = request.form.get("production_cost")
        pollution_level = request.form.get("pollution_level")
        net_capacity = request.form.get("net_capacity")
        resource_id = request.form.get("resource_select")
        org_id = request.form.get("org_select")
        region_id = request.form.get("region_select")

        data = Plants(
            plant_status = plant_status,
            spanned_area = spanned_area,
            production_cost = production_cost,
            pollution_level = pollution_level,
            net_capacity = net_capacity,
            resource_id = resource_id,
            org_id = org_id,
            region_id = region_id
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "plant"
            )
        else:
            db.session.commit()
            return redirect("/plant")

@app.route("/plant/<int:plant_id>/update", methods = ["GET", "POST"])
def update_plant(plant_id):
    try:
        plant_id = int(plant_id)
        old_data = Plants.query.get(plant_id)
        resource_list = Resource.query.all()
        organization_list = Organizations.query.all()
        region_list = Region.query.all()

        if request.method == "GET":
            return render_template(
                "update_plant.html",
                plant_id = plant_id,
                plant_status = old_data.plant_status,
                spanned_area = old_data.spanned_area,
                production_cost = old_data.production_cost,
                pollution_level = old_data.pollution_level,
                net_capacity = old_data.net_capacity,
                org_id = old_data.org_id,
                resource_id = old_data.resource_id,
                region_id = old_data.region_id,
                resource_list = resource_list,
                organization_list = organization_list,
                region_list = region_list
            )
        elif request.method == "POST":
            u_plant_status = request.form.get("status_select")
            u_spanned_area = request.form.get("spanned_area")
            u_production_cost = request.form.get("production_cost")
            u_pollution_level = request.form.get("pollution_level")
            u_net_capacity = request.form.get("net_capacity")
            u_resource_id = request.form.get("resource_select")
            u_org_id = request.form.get("org_select")
            u_region_id = request.form.get("region_select")

            # Update data
            old_data.plant_status = u_plant_status
            old_data.spanned_area = u_spanned_area
            old_data.production_cost = u_production_cost
            old_data.pollution_level = u_pollution_level
            old_data.net_capacity = u_net_capacity
            old_data.resource_id = u_resource_id
            old_data.org_id = u_org_id
            old_data.region_id = u_region_id

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
        return redirect("/plant")

@app.route("/plant/<int:plant_id>/delete", methods = ["GET", "POST"])
def delete_plant(plant_id):
    try:
        plant_id = int(plant_id)
        data = Plants.query.get(plant_id)

        # Flush from child

        dr_data = DailyReading.query.all()

        for dr in dr_data:
            if dr.plant_id == plant_id:
                try:
                    db.session.delete(dr)
                except:
                    return render_template(
                        "error.html"
                    )
                else:
                    db.session.commit()

        # Flush from parent

        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/plant")

    except:
        return render_template(
            "error.html"
        )

@app.route("/daily_reading", methods = ["GET", "POST"])
def view_daily_reading():
    reading_list = DailyReading.query.all()
    return render_template(
        "view_dr.html",
        reading_list = reading_list
    )

@app.route("/daily_reading/create", methods = ["GET", "POST"])
def create_dr():
    if request.method == "GET":
        plant_list = Plants.query.all()
        return render_template(
            "create_dr.html",
            plant_list = plant_list
        )
    elif request.method == "POST":
        plant_id = request.form.get("plant_select")
        date = request.form.get("date")
        energy_generated = request.form.get("energy_generated")

        data = DailyReading(
            plant_id = plant_id,
            date = date,
            energy_generated = energy_generated
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Daily Reading"
            )
        else:
            db.session.commit()
            return redirect("/daily_reading")

@app.route("/daily_reading/<int:plant_id>/<date>/update", methods = ["GET", "POST"])
def update_dr(plant_id, date):
    try:
        plant_id = int(plant_id)
        date = str(date)
        old_data = DailyReading.query.get((plant_id, date))
        plant_list = Plants.query.all()

        if request.method == "GET":
            return render_template(
                "update_dr.html",
                plant_list = plant_list,
                plant_id = old_data.plant_id,
                date = old_data.date,
                energy_generated = old_data.energy_generated
            )
        elif request.method == "POST":
            u_plant_id = request.form.get("plant_select")
            u_date = request.form.get("date")
            u_energy_generated = request.form.get("energy_generated")

            # Update data
            old_data.plant_id = u_plant_id
            old_data.date = u_date
            old_data.energy_generated = u_energy_generated

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
        return redirect("/daily_reading")

@app.route("/daily_reading/<int:plant_id>/<date>/delete", methods = ["GET", "POST"])
def delete_dr(plant_id, date):
    try:
        plant_id = int(plant_id)
        date = str(date)
        data = Plants.query.get((plant_id, date))
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/daily_reading")

    except:
        return render_template(
            "error.html"
        )

@app.route("/daily_demand", methods = ["GET", "POST"])
def view_dd():
    dd_list = DailyDemand.query.all()
    return render_template(
        "view_dd.html",
        daily_demand_list = dd_list
    )

@app.route("/daily_demand/create", methods = ["GET", "POST"])
def create_dd():
    if request.method == "GET":
        return render_template("create_dd.html")
    elif request.method == "POST":
        date = request.form.get("date")
        demand = request.form.get("demand")

        data = DailyDemand(
            date = date,
            demand = demand
        )

        try:
            db.session.add(data)
        except:
            db.session.rollback()
            return render_template(
                "exists.html",
                x = "Demand Date"
            )
        else:
            db.session.commit()
            return redirect("/daily_demand")

@app.route("/daily_demand/<date>/update", methods = ["GET", "POST"])
def update_dd(date):
    try:
        date = str(date)
        old_data = DailyDemand.query.get(date)

        if request.method == "GET":
            return render_template(
                "update_dd.html",
                date = old_data.date,
                demand = old_data.demand
            )
        elif request.method == "POST":
            u_demand = request.form.get("demand")

            # Update data
            old_data.demand = u_demand

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
        return redirect("/daily_demand")

@app.route("/daily_demand/<date>/delete", methods = ["GET", "POST"])
def delete_dd(date):
    try:
        date = str(date)
        data = DailyDemand.query.get(date)
        try:
            db.session.delete(data)
        except:
            return render_template(
                "error.html"
            )
        else:
            db.session.commit()
            return redirect("/daily_demand")

    except:
        return render_template(
            "error.html"
        )

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        debug=False,
        port=5000
    )