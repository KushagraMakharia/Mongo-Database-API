from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")

db = client.UserDb
users = db["Users"]

free_tokens = 10

def password_check(name, pwd):
	hashed = users.find({
		"Name": name
		})[0]["Password"]
	if bcrypt.checkpw(pwd.encode("utf8"), hashed):
		return True
	else:
		return False

def get_token(name):
	token = users.find({
		"Name": name
		})[0]["Tokens"]
	return token

# Adds new user and grants 10 free tokens for usage
class AddUser(Resource):
	def post(self):
		recv_json = request.get_json()
		name = recv_json["Name"]
		pwd = recv_json["Password"]
		hashed = bcrypt.hashpw(pwd.encode("utf8"), bcrypt.gensalt())
		users.insert_one({
			"Name": name,
			"Password": hashed,
			"Tokens": free_tokens,
			"Sentence": ""
			})

		retJson = {
		"Message": "User has been succesfully created.",
		"Status Code" : 200
		}

		return jsonify(retJson)

class Store(Resource):
	def post(self):
		recv_json = request.get_json()
		name = recv_json["Name"]
		pwd = recv_json["Password"]
		 
		if password_check(name, pwd):
			token = get_token(name)
			if token > 0:
				sentence = recv_json["sentence"]
				users.update_one({
					"Name": name
					}, {"$set":{
					"Sentence": sentence,
					"Tokens" : token - 1}
					})

				retJson = ({
					"Message": "Message stored succesfully.",
					"Status Code": 200
					})
				return jsonify(retJson)
			else:
				retJson = {
				"Status Code": 302
				}
				return jsonify(retJson)
		else:
			retJson = {
			"Status Code": 301
			}
			return jsonify(retJson)

class Retrive(Resource):
	def post(self):
		recv_json = request.get_json()
		name = recv_json["Name"]
		pwd = recv_json["Password"]
		
		if password_check(name, pwd):
			token = get_token(name) 
			if token > 0:
				sentence = users.find_one({
					"Name": name
					})["Sentence"]
				retJson = {
				"Message" : sentence,
				"Status Code" : 200
				}
				return jsonify(retJson)
			else:
				retJson = {
				"Status Code": 302
				}
				return jsonify(retJson)
		else:
			retJson = {
			"Status Code": 301
			}
			return jsonify(retJson)

class Test(Resource):
	def get(self):
		return "API is working."

api.add_resource(Test, "/test")
api.add_resource(AddUser, "/adduser")
api.add_resource(Store, "/store")
api.add_resource(Retrive, "/retrive")

if __name__ == "__main__":
	app.run(host='0.0.0.0')