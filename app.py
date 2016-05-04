from flask import Flask, render_template, request, redirect
import flask
import recommend
import json

app = Flask(__name__)

profileURL = ""
gamesJSON = {}
pFlag = False

@app.route('/')
def home():
	if(gamesJSON != {}):
		return render_template('home.html', flag=pFlag, testData=json.dumps(gamesJSON))
	else:
		return render_template('home.html', flag=pFlag, testData="")

@app.route("/analyze/", methods=['POST'])
def crunchProfile():
	global profileURL
	global pFlag
	profileURL = request.form['profileURL']
	if(profileURL == "" or not checkSteamURL(profileURL)):
		pFlag = False
	else:
		profileID = recommend.get_steamID64(profileURL) #get steam id from recommend.py
		recommend_stuff(profileID) #get json
		pFlag = True
	return redirect('/')

def recommend_stuff(profile_id): #gets the json result from recommend.py
	recommends = recommend.recommend(profile_id)
	games = []
	for rec in recommends:
		rec_dict = {"appId" : rec[2], "title": rec[3], "fromAppId": rec[0], "fromTitle":rec[1]}
		games.append(rec_dict)
	global gamesJSON
	gamesJSON = ({"games": games}) #json of recommendations
	writeJSONToDirectory(gamesJSON)

def writeJSONToDirectory(jsonArg): #just for reference
	fd = open('static/data.json', 'w')
	data = json.dumps(jsonArg)
	fd.write(data)
	fd.close()

def checkSteamURL(url):
	return "https://steamcommunity.com/id/" in url or "http://steamcommunity.com/id/" in url or "http://steamcommunity.com/profiles/" in url or "https://steamcommunity.com/profiles/" in url

if __name__ == "__main__":
	app.debug = True
	app.run()