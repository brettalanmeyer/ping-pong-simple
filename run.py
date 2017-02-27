from flask import Flask, render_template, Response, redirect, request
from flask.ext.assets import Environment, Bundle
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config.from_pyfile("config.cfg")
assets = Environment(app)
socketio = SocketIO(app)

data = {
	"button": "",
	"left": 0,
	"right": 0
}

@app.route("/", methods = ["GET"])
def index():
	return render_template("index.html", data = data)

@app.route("/new", methods = ["GET"])
def new():
	reset("none")
	return redirect("/")

@app.route("/", methods = ["POST"])
def create():
	global data
	data["games"] = int(request.form["games"])
	data["playto"] = int(request.form["playto"])
	return redirect("/")

@app.route("/buttons", methods = ["GET"])
def buttons():
	return render_template("buttons.html")

@app.route("/buttons/<path:button>/score", methods = ["POST"])
def score(button):
	global data

	data["button"] = button

	if button == "red" or button == "green":
		data["left"] += 1

	if button == "blue" or button == "yellow":
		data["right"] += 1

	socketio.emit("response", data, broadcast = True)

	return Response(json.dumps(data), status = 200, mimetype = "application/json")

@app.route("/buttons/<path:button>/undo", methods = ["POST"])
def undo(button):
	global data

	if data["left"] > 0 and (button == "red" or button == "green"):
		data["left"] -= 1

	if data["right"] > 0 and (button == "blue" or button == "yellow"):
		data["right"] -= 1

	socketio.emit("response", data, broadcast = True)

	return Response(json.dumps(data), status = 200, mimetype = "application/json")

@app.route("/buttons/<path:button>/reset", methods = ["POST"])
def reset(button):
	data["left"] = 0
	data["right"] = 0

	socketio.emit("response", data, broadcast = True)

	return Response(json.dumps(data), status = 200, mimetype = "application/json")

@app.errorhandler(404)
def not_found(error):
	return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
	return render_template("500.html"), 500

@socketio.on("connect", namespace = "/pingpong")
def ping_pong_connect():
	emit("response", data)

@socketio.on("disconnect", namespace = "/pingpong")
def ping_pong_disconnect():
	print("Client disconnected")

@socketio.on("broadcast", namespace = "/pingpong")
def ping_pong_message():
	emit("response", data, broadcast = True)

if __name__ == "__main__":
	socketio.run(app, host = app.config["HOST"], port = app.config["PORT"], debug = app.config["DEBUG"])
