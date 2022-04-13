from datetime import timedelta
from re import A
from flask import Flask, json, render_template, redirect, session, url_for,jsonify, flash
from flask_wtf import form
from itsdangerous.exc import SignatureExpired
from pymongo.message import query
from wtforms.validators import Email
from aggelia import Animal_Aggelia, Hospitality_Aggelia
import uuid
import base64
from flask_bootstrap import Bootstrap
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from pymongo import MongoClient
from user_forms import Register, Login
from passlib.hash import pbkdf2_sha256
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, timed
from flask_caching import Cache
import redis
import json
from report_form import ReportForm
from imagekitio import ImageKit
import os
from dotenv import load_dotenv

load_dotenv()

imagekit = ImageKit(
    private_key=    os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint =os.getenv("IMAGEKIT_ENDPOINT"),
)

app = Flask(__name__)
app.config.from_pyfile("config.cfg")


r = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"))

mail = Mail(app)
Bootstrap(app)
client = MongoClient(f"mongodb+srv://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@cluster0.yf9fk.mongodb.net/Aggelies?retryWrites=true&w=majority")
db = client.Aggelies
app.secret_key = b'\x06\xc9,}J\xbb[\\oO\xbd:\x98\x84\x1f\xdc\xa1\x10\xbf\x8AW0$e'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
s = URLSafeTimedSerializer("ThisIsASecret!")




def login_required(f): # login required
        @wraps(f)
        def wrap(*args, **kwargs):
            if "logged_in" in session:
                return f(*args, **kwargs)
            else:
                return redirect("/login/")
        return wrap




def start_session(user): # a function that starts the session
    session["logged_in"] = True
    session["user"] = user
    return redirect("/")


@app.route("/",  methods=["POST", "GET"])
@app.route("/<int:num>",  methods=["POST", "GET"])
def home_page(num=1):
    elements_per_page = 8
    if not r.exists(f"animal{num}"):
        pipeline = [
            {
                "$match": {
                    "found": False
                }
            },
            {
                "$skip": (num-1)*elements_per_page
            },
            {
                "$limit": elements_per_page
            },
        ]
        count_queries = db.Aggelies.count(query={"found": False})
        if count_queries <= elements_per_page:
            count = 1
        else:
            count = int(count_queries / elements_per_page + 1)
        animal_aggelies = list(db.Aggelies.aggregate(pipeline=pipeline))
        animal_aggelies.append(count)
        r.setex(f"animal{num}",timedelta(minutes=10) ,value=json.dumps(animal_aggelies))
        return render_template("index.html", aggelies=animal_aggelies[:-1], count=animal_aggelies[-1], num=num)
    else:
        animal_aggelies= json.loads(r.get(f"animal{num}"))
        # count_queries = db.Aggelies.count(query={"found": False})
        # count = int(count_queries / elements_per_page + count_queries % elements_per_page)
        return render_template("index.html", aggelies=animal_aggelies[:-1], count=animal_aggelies[-1], num=num)


@app.route("/hospitality/",  methods=["POST", "GET"])
@app.route("/hospitality/<int:num>",  methods=["POST", "GET"])
def hospitality(num=1):
    elements_per_page = 8
    if not r.exists(f"hospitality{num}"):
        pipeline = [
            {
                "$match": {
                    "full": False
                }
            },
            {
                "$skip": (num-1)*elements_per_page
            },
            {
                "$limit": elements_per_page
            },
        ]
        count_queries = db.hospitality.count({"full": False})
        if count_queries <= elements_per_page:
            count = 1
        else:
            count = int(count_queries / elements_per_page + 1)
        hospitality_aggelies = list(db.hospitality.aggregate(pipeline=pipeline))
        hospitality_aggelies.append(count)
        r.setex(f"hospitality{num}",timedelta(minutes=10) ,value=json.dumps(hospitality_aggelies))
        return render_template("hospitality.html", aggelies=hospitality_aggelies[:-1], count=count, num=num)
    else:
        hospitality_aggelies=json.loads(r.get(f"hospitality{num}"))
        # count_queries = db.hospitality.count(query={"full": False})
        # count = int(count_queries / elements_per_page + count_queries % elements_per_page)
        return render_template("hospitality.html", aggelies=hospitality_aggelies[:-1], count=hospitality_aggelies[-1],num=num)



@app.route("/hospitality-aggelia/",  methods=["POST", "GET"])
@login_required
def make_hospitality_post():
    form = Hospitality_Aggelia()
    if form.validate_on_submit():
        entry = {
            "_id": uuid.uuid4().hex,
            "username": session["user"]["username"],
            "name": form.name.data,
            "email": form.email.data,
            "species": form.species.data,
            "address": form.address.data,
            "contact_number": form.contact_number.data,
            "description": form.description.data,
            "full": False,
        }
        db.hospitality.insert_one(entry)
        return redirect("/hospitality/1")
    return render_template("hospitality_aggelia.html", form=form)






@app.route("/animal-aggelia/", methods=["POST", "GET"])
@login_required
def make_animal_post():
    form = Animal_Aggelia()
    if form.validate_on_submit():
        entry = {
            "_id": uuid.uuid4().hex,
            "username": session["user"]["username"],
            "name": form.name.data,
            "email": form.email.data,
            "photo_url": "" ,
            "species": form.species.data,
            "where_lost": form.where_lost.data,
            "when_lost": str(form.when_lost.data),
            "contact_number": form.contact_number.data,
            "description": form.description.data,
            "found": False,
        } 
        upload = imagekit.upload(file=base64.b64encode(form.photo.data.read()), file_name=entry["_id"], options={
            "use_unique_file_name": False,
        })
        print(upload)
        entry["photo_url"]=f"https://ik.imagekit.io/w4if3run6alm/{entry['_id']}"
        db.Aggelies.insert_one(entry)
        return redirect("/1")
    return render_template("animal_aggelia.html", form=form)



@app.route("/filter/<string:species>", methods=["POST", "GET"])
@app.route("/filter/<string:species>/<int:num>", methods=["POST", "GET"])
def by_species(species, num=1):
    elements_per_page = 8
    if not r.exists(f"filter_animal_{species}{num}"):
        if species =="dog" or species == "cat" or species=="other":
            pipeline = [
                {
                    "$match": {
                        "species": species,
                        "found": False
                    }
                },
                {
                    "$skip": (num-1)*elements_per_page
                },
                {
                    "$limit": elements_per_page
                },
            ]
            count_queries = db.Aggelies.count(query={"species": species ,"found": False})
            if count_queries < elements_per_page:
                count = 1
            else:
                count = int(count_queries / elements_per_page + 1)
            aggelies_by_species = list(db.Aggelies.aggregate(pipeline=pipeline))
            aggelies_by_species.append(count)
            r.setex(f"filter_animal_{species}{num}", timedelta(minutes=10), value=json.dumps(aggelies_by_species))
            return render_template("index.html", aggelies=aggelies_by_species[:-1], count=count, species=species)
        else:
            return "<h1>Invalid Species</h1>"
    else:
        aggelies_by_species = json.loads(r.get(f"filter_animal_{species}{num}"))
        # count_queries = db.Aggelies.count(query={"species": species ,"found": False})
        # count = int(count_queries/elements_per_page + count_queries%elements_per_page)
        return render_template("index.html", aggelies=aggelies_by_species[:-1], count=aggelies_by_species[-1], species=species)
    


@app.route("/my-posts/<string:username>", methods=["GET", "POST"])
@login_required
def my_posts(username):
    if username==session["user"]["username"]:
        if not r.exists(f"{username}_animal_posts") and not r.exists(f"{username}_hospitality_posts"):
            animal_aggelies = list(db.Aggelies.find({"username": session["user"]["username"]}))
            hospitality_aggelies = list(db.hospitality.find({"username": session["user"]["username"]}))
            r.setex(f"{username}_animal_posts", timedelta(minutes=10), value=json.dumps(animal_aggelies))
            r.setex(f"{username}_hospitality_posts", timedelta(minutes=10), value=json.dumps(hospitality_aggelies))
            return render_template("my_posts.html", animal_aggelies=animal_aggelies, hospitality_aggelies=hospitality_aggelies)
        else:
            animal_aggelies = json.loads(r.get(f"{username}_animal_posts"))
            hospitality_aggelies = json.loads(r.get(f"{username}_hospitality_posts"))
            return render_template("my_posts.html", animal_aggelies=animal_aggelies, hospitality_aggelies=hospitality_aggelies)
    else:
        return redirect(f"/my-posts/{session['user']['username']}")




@app.route("/animal-found-api/<string:bool>/<string:id>", methods=["POST", "GET"])
@login_required
def animal_found(bool, id):
    try:
        if session["logged_in"]:
            if bool == "1":
                if db.Aggelies.find_one_and_update({"_id": id, "username": session["user"]["username"]}, [{"$set": {"found": True}}]):
                    return "<h1>Updated</h1>"
                else:
                    return "<h1>Failed</h1>"
            elif bool == "0":
                if db.Aggelies.find_one_and_update({"_id": id, "username": session["user"]["username"]}, [{"$set": {"found": False}}]):
                    return "<h1>Updated</h1>"
                else:
                    return "<h1>Failed</h1>"
        else:
            return "<h1> Can't Update </h1>"
    except Exception:
        return "<h1>Σφάλμα</h1>"


@app.route("/hospitality-full/<string:bool>/<string:id>", methods=["POST", "GET"])
@login_required
def hospitality_full(bool, id):
    try:
        if session["logged_in"]:
            if bool == "1":
                if db.hospitality.find_one_and_update({"_id": id, "username": session["user"]["username"]}, [{"$set": {"full": True}}]):
                    return "<h1>Updated</h1>"
                else:
                    return "<h1>Failed</h1>"
            elif bool == "0":
                if db.hospitality.find_one_and_update({"_id": id, "username": session["user"]["username"]}, [{"$set": {"full": False}}]):
                    return "<h1>Updated</h1>"
                else:
                    return "<h1>Failed</h1>"
        else:
            return "<h1> Can't Update </h1>"
    except Exception:
        return "<h1>Σφάλμα</h1>"



@app.route("/delete-animal-api/<string:id>", methods=["POST", "GET"])
@login_required
def delete_animal_post(id):
    try:
        if session["logged_in"]:
            if db.Aggelies.delete_one({"_id": id, "username": session["user"]["username"]}):
                return "<h1>Deleted</h1>"
            else:
                return "<h1>Not Found</h1>"
    except:
        return "<h1>Σφάλμα</h1>"


@app.route("/delete-hospitality-api/<string:id>", methods=["POST", "GET"])
@login_required
def delete_hospitality_post(id):
    try:
        if session["logged_in"]:
            if db.hospitality.delete_one({"_id": id, "username": session["user"]["username"]}):
                return "<h1>Deleted</h1>"
            else:
                return "<h1>Not Found</h1>"
    except:
        return "<h1>Σφάλμα</h1>"


@app.route("/animal/<string:id>",  methods=["POST", "GET"])
def animal_post(id):
    if not r.exists(f"animal{id}"):
        Aggelia = db.Aggelies.find_one({"_id": id})
        if Aggelia:
            r.setex(f"animal{id}", timedelta(hours=2), json.dumps(Aggelia))
            return render_template("animal_aggelia_id.html", Aggelia = Aggelia)
        else:
            return "<h1>There is no such Post</h1>"
    else:
        return render_template("animal_aggelia_id.html", Aggelia=json.loads(r.get(f"animal{id}")))



@app.route("/hospitality/<string:id>",  methods=["POST", "GET"])
def hospitality_post(id):
    if not r.exists(f"hospitality{id}"):
        Aggelia = db.hospitality.find_one({"_id": id})
        if Aggelia:
            r.setex(f"hospitality{id}", timedelta(hours=2), json.dumps(Aggelia))
            return render_template("hospitality_aggelia_id.html", Aggelia = Aggelia)
        else:
            return "<h1>There is no such Post</h1>"
    else:
        return render_template("hospitality_aggelia_id.html", Aggelia=json.loads(r.get(f"hospitality{id}")))
#------------------------------------------------

@app.route("/register/", methods=["POST", "GET"])
def register():
    form = Register()
    if form.validate_on_submit():
        user = {
            "_id": uuid.uuid4().hex,
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "username": form.username.data,
            "email": form.email.data,
            "password": form.password.data,
            "email_confirmed": False,
            "token": "",
        }
        if form.password.data != form.password_confirm.data:
            flash("Οι κωδικόι δεν ειναι ίδιοι.")
        elif db.users.find_one({ "username": user["username"], "email_confirmed": True}):
            flash( "Αυτό το username χρησιμοποιείται ήδη.")
        elif db.users.find_one({ "email": user["email"], "email_confirmed": True}):
            flash("Αυτό το email χρησιμοποιείται ήδη.")
        else:
            email = user["email"]
            token = s.dumps(email, salt="email-confirm")
            user["password"] = pbkdf2_sha256.encrypt(user["password"])
            user["token"] = token
            msg = Message("No-Reply", sender="aggeliesgiafotia@gmail.com", recipients=[email])
            link = url_for("confirm_email", token=token, _external=True)
            msg.body = "<h3>Κάντε click στο link για να επιβεβαιώσετε τον λογαριασμό σας <b>{}</b></h3>".format(link)
            mail.send(msg)
            if db.users.find_one_and_update({"email": email}, {"$set": {"token": token}}):
                flash("Στάλθηκε ο συνδεσμος επαληθευσης στο email σας. Κοιτάξτε και στα ΣΠΑΜ!")
            else:
                db.users.insert_one(user)
            flash("Στάλθηκε ο σύνδεσμος επαλήθευσης στο email σας. Κοιτάξτε και στα ΣΠΑΜ!")
    return render_template("register.html", form=form)




@app.route("/login/", methods=["POST", "GET"])
def login():
    form = Login()
    if form.validate_on_submit():
        user =  db.users.find_one({"username": form.username.data})
        if user and user["email_confirmed"] == False:
            flash("Ο Λογαριασμός σας δεν εχει επιβεβαιωθεί.")
        elif user and pbkdf2_sha256.verify(form.password.data, user["password"]):
            return start_session(user)
        else:
            flash("Δεν βρέθηκε χρήστης με αυτα τα στοιχεία.")
    return render_template("login.html", form=form)


@app.route("/logout/", methods=["POST", "GET"])
@login_required
def signout():
        session.clear()
        return redirect("/")


@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
        user = db.users.find_one_and_update({"token": token}, [{"$set": {"email_confirmed": True}}, {"$unset": "token"}])
    except SignatureExpired:
        return f"<h3>Το λινκ επαλήθευσης έχει λήξει, για να γραφτείται πατήστε <a href='{url_for('register')}'>εδώ></a></h3>"
    return f"<h3>Ο λογαριασμός σας επιβεβαιώθηκε.<a href='{url_for('login')}'>Συνδεθείτε.</a></h3>"



@app.route("/report/<string:dbstring>/<string:id>", methods=["POST", "GET"])
def report(dbstring, id):
    if dbstring == "animals" or dbstring == "hospitality":
        form = ReportForm()
        if form.validate_on_submit():
            if db.reports.find_one_and_update(filter={"db": dbstring,"reported_id": id},update={'$push': {"description": form.description.data}}):
                return redirect(url_for("home_page"))
            else:
                entry = {
                "reported_id": id,
                "db": dbstring,
                "description": [form.description.data],
            }
                db.reports.insert_one(entry)
                return redirect(url_for("home_page"))
        return render_template("report.html", form=form)
    else:
        return "<h1>Σφάλμα</h1>"
    

@app.route("/info/", methods=["GET", "POST"])
def contact():
    return render_template("contact_info.html")
