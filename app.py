from flask import Flask, render_template, request, redirect
import flask
import recommend

app = Flask(__name__)

profileURL = "Test"
gameJSON = {}

@app.route('/')
def home():
	return render_template('display.html')

@app.route("/analyze/", methods=['POST'])
def crunchProfile():
	global profileURL
	profileURL = request.form['profileURL']
	
	profileID = recommend.get_steamID64(profileURL)
	recommend_stuff(profileID)
	return redirect('/')

def recommend_stuff(profile_id):
	recommends = recommend.recommend(profile_id)
	games = []
	for rec in recommends:
		rec_dict = {"appId" : rec[2], "title": rec[3], "fromAppId": rec[0], "fromTitle":rec[1]}
		games.append(rec_dict)
	global gameJSON
	gameJSON = flask.jsonify({"games": games})


if __name__ == "__main__":
	app.debug = True
	app.run()