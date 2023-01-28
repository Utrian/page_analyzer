import os
from flask import Flask
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def main():
    return "<h1>Hello!</h2>"
