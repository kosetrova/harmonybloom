#importing libraries
from flask import Flask, render_template, request
from flower import gpt_find_song
import re


#creating a Flask app
app = Flask(__name__)

# 'starter question'
new_question="Hi, what do I need to input to know about my birth flower?"

#defining a default route ('/') with GET method
@app.route('/')
def index():
	question="question"
	response = gpt_find_song(new_question)
	return render_template("index.html", bot_response = response[0])


#handling POST requests to the default route
@app.route('/', methods = ['POST'])
def index_post():
	question = request.form['question']
	response = gpt_find_song(question)
	#matches = re.findall(r'\((.*?)\)', str(response))
	return render_template("index.html", bot_response = response[0], embed_link=response[1])
