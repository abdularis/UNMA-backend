import os
import logging

from flask import Flask, redirect, url_for

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

app.config.update(
    SECRET_KEY=b'sldf9238r48fhersASDfdf38r948fjF3498fjdFf4'
)
app.config.from_json('config/db_config.json')
app.config.from_json('config/fcm_config.json')
app.config.from_json('config/path_config.json')


import unma.api
import unma.admin
app.register_blueprint(unma.api.api)
app.register_blueprint(unma.admin.admin)


@app.route('/')
def index():
    return redirect(url_for('admin.login'))
