# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps.home.models import Videos
from apps.home.models import DetectTime
from apps import db
import os
from os.path import dirname, realpath
from flask import current_app
from werkzeug.utils import secure_filename

from apps.predict_on_video import predict_on_video, SEQUENCE_LENGTH


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        msg = ""
        if 'msg' in request.args:
            msg = request.args['msg']

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        data = Videos.query.order_by(Videos.upload_time.desc()).all()

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment, data=data, add_video=msg)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/videos/<src>')
@login_required
def videos_player(src):
    segment = get_segment(request)
    video = Videos.query.filter_by(video_id=src).first()
    data = DetectTime.query.filter_by(video_id=src).order_by(DetectTime.time).all()
    violatedActionNo = len([x for x in data if x.action == 'fight'])
    video_name = os.path.splitext(os.path.basename(src))[0]
    contain_suspicous_activies = len(list(filter(lambda x: x.action == 'lifting' or x.action == 'stealing', data))) > 0
    return render_template('home/video-players.html',
                           segment=segment,
                           data=data,
                           video_name = video_name,
                           violatedActionNo = violatedActionNo,
                           contain_suspicous_activies = contain_suspicous_activies,
                           video = video,
                           src=src)


@blueprint.route('/upload-video', methods=['POST'])
@login_required
def success():
    if request.method == 'POST':
        msg = ""
        f = request.files['file']

        if not f:
            return return_home(request, msg)

        filename = secure_filename(f.filename)

        print(f"UPLOAD_FOLDER_ROUTE: {current_app.config['UPLOAD_FOLDER']}")
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        print(save_path)
        try:
            f.save(save_path)
        except Exception as e:
            print('Error in saving file')
            print(e)
        output_path, result, detects, total_seconds = predict_on_video(save_path, SEQUENCE_LENGTH)

        print(detects)
        print(result)
        # Cleanup
        # os.remove(save_path)
        # print(f"File '{save_path}' deleted successfully.")

        filename = os.path.basename(output_path)
        video = Videos.query.filter_by(video_id=filename).first()
        if not video:
            video = Videos(video_id=filename, labels=", ".join(result), length=total_seconds)
            db.session.add(video)

            for detect_time in detects:
                print(detect_time)
                detects = DetectTime(video_id=filename, time=f"{detect_time[0]:02d}:{detect_time[1]:02d}", action=detect_time[2], image=detect_time[3])
                db.session.add(detects)

            db.session.commit()

            msg = "Add Video Successfully"

        # return return_home(request, msg)
        return videos_player(video.video_id)


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


def return_home(request, msg):
    segment = get_segment(request)

    data = Videos.query.order_by(Videos.upload_time.desc()).all()

    # return render_template("home/dashboard.html", segment=segment, data=data, add_video=msg)
    return redirect(url_for("home_blueprint.route_template", template = 'dashboard', msg=msg))
