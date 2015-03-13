# This is my model file. My class definitions, reused functions, 
# etc. will live here. 

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import date
from datetime import datetime

ENGINE = create_engine("sqlite:///runfree.db", echo=False)
sqla_session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = sqla_session.query_property()


#
# Classes
#

class User(Base):

	__tablename__ = "users"

	id = Column(Integer, primary_key = True)
	email = Column(String(64), unique = True, nullable = False)
	password = Column(String(64), nullable = True)
	first = Column(String(64), nullable = True)
	last = Column(String(64), nullable = True)
	birthdate = Column(DateTime(timezone = False), nullable = True)
	sex = Column(String(15), nullable = True)
	zipcode = Column(String(15), nullable = True)

	runs = relationship("Run", backref=backref("user"))
	goals = relationship("Goal", backref=backref("user"))
	

	def __repr__(self):
		return "User with email: %s" % self.email

class Run(Base):

	__tablename__ = "runs"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("users.id"))
	date_run = Column(DateTime(timezone = False), nullable = True)
	zipcode = Column(String(16), nullable = True)
	approx_dist = Column(Float, nullable = True)
	approx_time = Column(Integer, nullable = True)
	commit_date = Column(DateTime(timezone = False), nullable = False)
	route = Column(Integer, ForeignKey("routes.id"), nullable = True)

	ratings = relationship("Rating", backref=backref("run"))
 
	def __repr__(self):
		return "Run on %s" % datetime.strptime((str(self.date_run)), "%Y-%m-%d %H:%M:%S").strftime("%m-%d-%Y")

class Question(Base):

	__tablename__ = "questions"

	id = Column(Integer, primary_key = True)
	question = Column(String(200), nullable = False)
	minimum = Column(Integer, nullable = True)
	maximum = Column(Integer, nullable = True)

	def __repr__(self):
		return "%s" % self.question

class Rating(Base):

	__tablename__ = "ratings"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("users.id"))
	run_id = Column(Integer, ForeignKey("runs.id"))
	question_id = Column(Integer, ForeignKey("questions.id"))
	numeric_ans = Column(Integer, nullable = True)
	select_ans = Column(String(100), nullable = True)
	text_ans = Column(Text, nullable = True)

	def __repr__(self):
		return "User ID: %d, Run ID: %d, Question ID: %d" % (self.user_id, self.run_id, self.question_id)

class Goal(Base):

	__tablename__ = "goals"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("users.id"))
	description = Column(String(200), nullable = False)
	fitness_level = Column(String(200))
	run_length_history = Column(String(15))
	set_date = Column(DateTime(timezone = False), nullable = False)
	zipcode = Column(String(15))
	race_url = Column(String(200))
	event_date = Column(DateTime(timezone = False))
	id_for_api = Column(String(100))
	date_completed = Column(DateTime(timezone = False), nullable = True)

	def __repr__(self):
		return "User: %d, Goal: %s" % (self.user_id, self.description)


class Subgoal(Base):

	__tablename__ = "subgoals"

	id = Column(Integer, primary_key = True)
	goal_id = Column(Integer, ForeignKey("goals.id"))
	description = Column(String(200), nullable = True)
	date = Column(DateTime(timezone = False), nullable = True)
	date_completed = Column(DateTime(timezone = False), nullable = True)
	associated_run_id = Column(Integer, nullable = True)

	goal = relationship("Goal", backref=backref("subgoals", order_by = id))
	
	def __repr__(self):
		return "%s" % self.description

class Route(Base):

	__tablename__ = "routes"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey("users.id"))
	title = Column(String(200), nullable = False)
	location_description = Column(String(500))
	notes = Column(Text, nullable = True)
	distance = Column(Float, nullable = True)
	html_embed = Column(Text, nullable = False)

	user = relationship("User", backref = backref("routes", order_by = id.desc()))

	def __repr__(self):
		return "%s : %f Miles" % (self.location_description, self.distance)



# -----------Classes End--------------------------

#
# functions
#

def insert_new_user(new_user):
	
	"""Will insert a new user into the database when he
	or she signs up."""
	sqla_session.add(new_user)
	sqla_session.commit()

def get_user_by_email(email):
	"""Returns the user object associated with an email address."""
	
	user = sqla_session.query(User).filter_by(email=email).one()
	
	return user

def insert_new_run(new_run):
	"Will insert a new run into the database for the user."
	sqla_session.add(new_run)
	sqla_session.commit()

def get_latest_run(user):
	"""Will find a run with a particular time stamp."""
	run = sqla_session.query(Run).filter_by(user_id = user.id).order_by(Run.commit_date.desc()).first()

	return run

def get_run_by_id(run_id):
	"""Will find a run with the indicated run_id."""
	run = sqla_session.query(Run).filter_by(id=run_id).first()

	return run

def find_all_runs(user):
	"""Returns a list of all the users runs"""

	runs = sqla_session.query(Run).filter_by(user_id = user.id).all()

	return runs

def find_all_runs_desc(user):
	"""Returns a list of all the users runs newest first."""

	runs = sqla_session.query(Run).filter_by(user_id = user.id).order_by(Run.date_run.desc()).all()

	return runs


def insert_new_goal(new_goal):
	"""Will insert a new goal into the database."""
	sqla_session.add(new_goal)
	sqla_session.commit()

def insert_new_subgoal(subgoal):
	"""Will insert a new subgoal into the database."""
	sqla_session.add(subgoal)
	sqla_session.commit()

def get_most_recent_goal(user):
	"""Finds the most recent goal for the user."""
	goal = sqla_session.query(Goal).filter_by(user_id = user.id).order_by(Goal.set_date.desc()).first()
	return goal

def get_goal_by_id(goal_id):
	"""Will find a goal with the indicated goal_id."""
	goal = sqla_session.query(Goal).filter_by(id=goal_id).first()

	return goal

def get_subgoals_by_goal_id(goal_id):
	"""will get all the subgoals for a given goal."""
	subgoals = sqla_session.query(Subgoal).filter_by(goal_id=goal_id).all()

	return subgoals

def get_subgoal_by_id(subgoal_id):
	""""will get the subgoal object for a given id."""
	subgoal = sqla_session.query(Subgoal).filter_by(id = subgoal_id).one()

	return subgoal

def get_all_goals(user):
	"""returns a lis of all goals for the given user."""
	goals = sqla_session.query(Goal).filter_by(user_id = user.id).all()

	return goals

def get_outstanding_subgoals(user):
	"""returns a list of outstanding subgoal objects"""
	goals = get_all_goals(user)
	outstanding_subgoals = []

	for goal in goals:
		subgoals = get_subgoals_by_goal_id(goal.id)
		for subgoal in subgoals:
			if not subgoal.date_completed:
				outstanding_subgoals.append(subgoal)

	return outstanding_subgoals

def get_outstanding_subgoal_by_goal_id(goal_id):
	"""Returns outstanding subgoals for a particular goal."""

	subgoals = get_subgoals_by_goal_id(goal_id)
	outstanding_subgoals = []
	for subgoal in subgoals:
		if not subgoal.date_completed:
			outstanding_subgoals.append(subgoal)

	return subgoals


def get_runs_after_date(user, date):
	"""gets all runs for a user after a given date."""
	all_runs = find_all_runs(user)
	runs_after_date = []
	for run in all_runs:
		if run.date_run > date:
			runs_after_date.append(run)

	return runs_after_date

def get_ratings_for_run(run_id):
	"""returns all ratings for a given run."""
	ratings = sqla_session.query(Rating).filter_by(run_id = run_id).all()

	return ratings

def get_location_by_run_id(run_id):
	""""returns the location of a run with the provided run id. """

	location = sqla_session.query(Rating).filter_by(run_id = run_id, question_id = 6).one()

	return location

def get_terrain_by_run_id(run_id):
	"""returns the terrain of a run with the provided run id. """

	terrain = sqla_session.query(Rating).filter_by(run_id = run_id, question_id = 7).one()

	return terrain

def get_route_by_run_id(run_id):
	"""returns the route type for a run with the provided run id."""

	route = sqla_session.query(Rating).filter_by(run_id = run_id, question_id = 8).one()

	return route

def get_instagram(run_id):
	"""Returns the instagram html for a given run."""

	instagram = sqla_session.query(Rating).filter_by(run_id = run_id, question_id = 10).all()

	return instagram

def get_location_ratings(user, runs_to_get = 5):
	""" Returns all ratings that deal with location for a 
	given user. """

	runs = get_collection_of_runs(user.id, runs_to_get = runs_to_get)

	location_ratings = []

	for run in runs:
		location_ratings.append(sqla_session.query(Rating).filter_by(question_id = 6, user_id = user.id, run_id = run[3]).one())
	

	return location_ratings

def get_collection_of_runs(user_id, runs_to_get = 5):

	"""Returns the date and distance of the latest runs 
	for a given user. """

	runs = sqla_session.query(Run.date_run, Run.approx_dist, Run.id).filter_by(user_id = user_id).order_by(Run.date_run.desc()).limit(runs_to_get).all()

	# Untuple-ing
	run_list = []

	for run in runs:
		run_list.append([run[0], run[1], get_run_score(run[2]), run[2]])

	return run_list

def get_run_score(run_id):
	"""Returns a score that will help me rate the quality of the run."""

	during_score = sqla_session.query(Rating.numeric_ans).filter_by(run_id = run_id, question_id = 2).first()
	after_score = sqla_session.query(Rating.numeric_ans).filter_by(run_id = run_id, question_id = 3).first()
	energy_score = sqla_session.query(Rating.numeric_ans).filter_by(run_id = run_id, question_id = 4).first()

	run_score = .50 * during_score[0] + .20 * after_score[0] + .30 * energy_score[0]

	return run_score

def get_before_ratings(user, runs_to_get = 5):
	"""returns  list of all the user inputted ratings about how they felt before the run."""
	
	runs = get_collection_of_runs(user.id, runs_to_get = runs_to_get)

	mood_ratings = []
	mood_info = []
	
	for run in runs:
		mood_ratings.append(sqla_session.query(Rating).filter_by(run_id = run[3], question_id = 1).one())

	print mood_ratings
	
	for mood in mood_ratings:
		mood_info.append([mood.numeric_ans, mood.run.approx_dist])

	return mood_info

def get_during_ratings(user, runs_to_get = 5):
	"""return list of all the user inputted ratings about how they felt during the run. """
	runs = get_collection_of_runs(user.id, runs_to_get = runs_to_get)

	mood_ratings = []
	mood_info = []

	for run in runs:
		mood_ratings.append(sqla_session.query(Rating).filter_by(run_id = run[3], question_id = 2).one())

	for mood in mood_ratings:
		mood_info.append([mood.numeric_ans, mood.run.approx_dist])

	return mood_info

def get_after_ratings(user, runs_to_get = 5):
	"""returns list of all the user inputted ratings about how they felt after the run."""

	runs = get_collection_of_runs(user.id, runs_to_get = runs_to_get)

	mood_ratings = []

	for run in runs:
		mood_ratings.append(sqla_session.query(Rating).filter_by(run_id = run[3], question_id = 3).one())
	
	mood_info = []

	for mood in mood_ratings:
		mood_info.append([mood.numeric_ans, mood.run.approx_dist])

	return mood_info

def get_user_routes(user):
	"""returns all the route objects for the given user. """

	routes = sqla_session.query(Route).filter_by(user_id = user.id).all()

	return routes

def get_route_by_id(route_id):
	"""returns a route object for the given id."""

	route = sqla_session.query(Route).filter_by(id=route_id).one()

	return route
	
def create_db():
	"""Recreates the database."""

	Base.metadata.create_all(ENGINE)

# Dictionaries, etc. that will be helpful in displaying info

route_dictionary = {
	"point_to_point": "Point to point",
	"out_and_back": "Out and back",
	"treadmill": "Treadmill", 
	"track": "Track",
	"random": "Random, rambling route"
}

terrain_dictionary = {
	"flat": "Flat", 
	"downhill": "Mostly Downhill",
	"uphill": "Mostly Uphill",
	"hills": "Rolling Hills"
}

location_dictionary = {
	"park": "Park", 
	"city": "City", 
	"neighborhood": "Neighborhood", 
	"trail": "Trail", 
	"beach": "Beach", 
	"treadmill": "Treadmill", 
	"track": "Track"
}

goal_dictionary = {
	"run_walk_5k": "Run/Walk 5k", 
	"run_5k": "Run 5k", 
	"run_walk_10k": "Run/Walk 10k", 
	"run_10k": "Run 10k", 
	"run_walk_half": "Run/Walk Half Marathon (13.1 Miles)", 
	"run_half": "Run Half Marathon (13.1 Miles)", 
	"run_walk_1_mile": "Run/Walk 1 mile", 
	"run_walk_2_miles": "Run/Walk 2 miles", 
	"run_walk_3_miles": "Run/Walk 3 miles", 
	"run_2_miles": "Run 2 miles", 
	"run_walk_5_miles": "Run/Walk 5 miles", 
	"run_5_miles": "Run 5 miles", 
	"run_walk_10_miles": "Run/Walk 10 miles", 
	"run_10_miles": "Run 10 miles"
}

subgoal_dictionary = {
	"run_walk_5k": ["run_walk_1_mile", "run_walk_2_miles"], 
	"run_5k": ["run_walk_1_mile", "run_walk_2_miles", "run_walk_3_miles", "run_2_miles"],
	"run_walk_10k": ["run_walk_5k", "run_walk_5_miles"],
	"run_10k": ["run_walk_5k", "run_5k", "run_walk_10k", "run_5_miles"], 
	"run_walk_half": ["run_walk_5k", "run_walk_10k", "run_walk_10_miles"], 
	"run_half": ["run_walk_5k", "run_walk_10k", "run_5k", "run_10k", "run_walk_10_miles", "run_10_miles"]
}

distance_dictionary = {
	"run_walk_5k": "Distance%20(running):5k", 
	"run_5k": "Distance%20(running):5k", 
	"run_walk_10k": "Distance%20(running):10k", 
	"run_10k": "Distance%20(running):10k", 
	"run_walk_half":"Distance%20(running):half%20marathon", 
	"run_half": "Distance%20(running):half%20marathon"
}

distance_int_dictionary = {
	"run_walk_5k": 3, 
	"run_5k": 3, 
	"run_walk_10k": 6, 
	"run_10k": 6, 
	"run_walk_half": 13, 
	"run_half": 13, 
	"run_walk_1_mile": 1, 
	"run_walk_2_miles": 2, 
	"run_walk_3_miles": 3, 
	"run_2_miles": 2, 
	"run_walk_5_miles": 5, 
	"run_5_miles": 5, 
	"run_walk_10_miles": 10, 
	"run_10_miles": 10
}

location_badges_dictionary = {

	"park": "/static/images/hayleypark.jpg", 
	"city": "/static/images/citybadge.jpg", 
	"neighborhood": "static/images/hayleyneighborhood.jpg", 
	"trail": "/static/images/hayleymountainterrain.jpg", 
	"beach": "/static/images/beachbadge.jpg", 
	"treadmill": "static/images/treadmillbadge.jpg", 
	"track": "static/images/trackbadge.jpg"
	
}

terrain_badges_dictionary = {
	"flat": "/static/images/hayleypark.jpg", 
	"downhill": "/static/images/hayleypark.jpg",
	"uphill": "/static/images/hayleypark.jpg",
	"hills": "/static/images/hayleypark.jpg"

}

route_badges_dictionary = {
	"point_to_point": "/static/images/hayleypark.jpg",
	"out_and_back": "/static/images/hayleypark.jpg",
	"treadmill": "/static/images/hayleypark.jpg", 
	"track": "/static/images/hayleypark.jpg",
	"random": "/static/images/hayleypark.jpg"
}

weekday_badges_dictionary = {
	"Monday": "/static/images/hayleypark.jpg",
	"Tuesday": "/static/images/hayleypark.jpg",
	"Wednesday": "/static/images/hayleypark.jpg", 
	"Thursday": "/static/images/hayleypark.jpg",
	"Friday": "/static/images/hayleypark.jpg",
	"Saturday": "/static/images/hayleypark.jpg",
	"Sunday": "/static/images/hayleypark.jpg"
}
