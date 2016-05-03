from flask import Flask, render_template, request, redirect
import flask
import recommend

app = Flask(__name__)

profileURL = "Test"
gameJSON = {}

@app.route('/')
def home():
	return render_template('home.html')

@app.route("/analyze/", methods=['POST'])
def crunchProfile():
	global profileURL
	profileURL = request.form['profileURL']
	
	profileID = recommend.get_steamID64(profileURL) #get steam id from recommend.py
	recommend_stuff(profileID) #get json
	return render_template('display.html', data=gameJSON) #render template, pass in json

def recommend_stuff(profile_id): #gets the json result from recommend.py
	recommends = recommend.recommend(profile_id)
	games = []
	for rec in recommends:
		rec_dict = {"appId" : rec[2], "title": rec[3], "fromAppId": rec[0], "fromTitle":rec[1]}
		games.append(rec_dict)
	global gameJSON
	gameJSON = flask.jsonify({"games": games}) #json of recommendations


if __name__ == "__main__":
	app.debug = True
	app.run()