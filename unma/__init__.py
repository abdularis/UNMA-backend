# __init__.py.py
# Created by abdularis on 08/10/17

import os
import logging

from flask import Flask, redirect, url_for

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

app.config.update(
    FCM_SERVER_KEY='AAAA8vB1upQ:APA91bF2ilOYFmf1DRJJ9o5Ug4aYSvoewUkqr3xvUzozePrPUyjiXUlr-8kiBMyZyMzgV01l77G-y_z_MkfMtyN3UEVGPxzp6wK4WYctMVHTi3lLFB0l_86_B6CClDfckTVNB7Ex71A0',
    SECRET_KEY=b'sldf9238r48fhersASDfdf38r948fjF3498fjdFf4',
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'media'),
    DATABASE='sqlite:///%s' % os.path.join(app.instance_path, 'data.db')
)

import unma.api
import unma.admin
app.register_blueprint(unma.api.api)
app.register_blueprint(unma.admin.admin)


@app.route('/')
def index():
    return redirect(url_for('admin.login'))
