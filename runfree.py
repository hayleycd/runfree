# This is the controller file. All of my routes for my flask app
# will go here. 

from flask import Flask, request, render_template, g, redirect, url_for, flash
from flask import session as flask_session
import model
import jinja2
import os
from datetime import datetime

# App information

app = Flask(__name__)
app.secret_key = "THISISMYPRODUCTIONANDTESTINGKEY"
app.jinja_env.undefined = jinja2.StrictUndefined

# Routes Begin Here

# These Routes are for navigating before you log in. 

@app.route("/")
def landing_page():
	return render_template("landing.html")

@app.route("/about")
def about_runfree():
	return render_template("about_runfree.html")

@app.route("/business")
def display_business_info():
	return render_template("business_card.html")


# These Routes are for logging in. 

@app.route("/authenticate", methods=["POST"])
def authenticate_user():
	# gets email and password
	email = request.form.get("email")
	password = request.form.get("password")
	user = model.get_user_by_email(email)

	# if email not in the database, redirects to a sign up page.
	if user == None:
		flash("Please sign up!")
		
		return redirect("/new_user")
	
	# if password does not match what is in the database, asks user to try again.  
	if user.password != password:
		flash("The password you entered is incorrect. Please try again.")

		return redirect("/")
	
	# adds email to session. Redirects to run_log. 
	flask_session["email"] = model.get_user_by_email(email).email
	flash("Successfully logged in!")

	return redirect("/run_log")

@app.route("/new_user")
def add_user():
	return render_template("new_user.html")

@app.route("/add_user", methods=["POST"])
def insert_user():

	# Pulling out all the info from the sign up form. 

	email = request.form.get("email")
	password = request.form.get("password")
	passwordcheck = request.form.get("passwordcheck")
	first = request.form.get("first_name")
	last = request.form.get("last_name")
	birthdate = request.form.get("birthdate")
	# Converting the birthdate to a datetime object.
	birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
	sex = request.form.get("sex")

	# Checking to be sure that the user entered the password as desired.
	# Will redirect them back to the form if not. 
	if password != passwordcheck:
		flash("Your passwords do not match. Please refill out the form.")
		return redirect("/new_user")

	# Checking to be sure that the new user filled out the form in its entirety.
	# Will redirect them back to the form if not. 

	user_info = [email, password, first, last, birthdate, sex]
	print user_info

	if None in user_info:
		flash("You must fully fill out the form. Please try again.")
		return redirect("/new_user")

	# Creating a user object with the user's information. 
	new_user = model.User(email=email, password=password, first=first, last=last, birthdate=birthdate, sex=sex )
	
	# Adding the user to the database. 
	model.insert_new_user(new_user)

	# storing their email in the session. 
	flask_session["email"] = email

	return redirect("/run_log")

# These Routes are for navigating the functionality 
# of the app once you are logged in. 

@app.route("/run_log")
def display_log():
	if flask_session.get("email") == None:
		flash("You must sign in to view that page.")
		
		return redirect("/")
	
	else:
		user = model.get_user_by_email(flask_session["email"])

		runs = model.find_all_runs(user)


		return render_template("run_log.html", user = user, runs = runs)

@app.route("/new_run")
def new_run():
	return render_template("new_run.html")

@app.route("/add_run", methods = ["POST"])
def add_run():
	date_run = request.form.get("new_run_date")
	time_run = request.form.get("new_run_time")
	user = model.get_user_by_email(flask_session["email"])
	
	date_run = datetime.strptime(date_run, "%Y-%m-%d")
	new_run = model.Run(user_id = user.id, date_run = date_run)
	model.insert_new_run(new_run)
	
	return redirect("/run_log")


@app.route("/run_graphs")
def display_progress():
	
	return render_template("data_vis.html")


@app.route("/goals")
def set_goals():
	
	return render_template("goal_log.html")


# These Routes are for logging you out. 

@app.route("/sign_out")
def end_session():

	flask_session.pop("email", None)

	return redirect("/")







if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)