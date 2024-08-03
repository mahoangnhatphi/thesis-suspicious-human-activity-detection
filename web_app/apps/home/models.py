# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps import db
from sqlalchemy.sql import func
from sqlalchemy import Text

class Videos(db.Model):

    __tablename__ = 'videos'

    id            = db.Column(db.Integer, primary_key=True)
    video_id      = db.Column(db.String(255), unique=True, nullable=False)
    labels        = db.Column(db.String(255), nullable=True)
    upload_time   = db.Column(db.DateTime(timezone=True), server_default=func.now())
    length        = db.Column(db.Integer, unique=False, nullable=False)

    # def __init__(self, **kwargs):
    #     for property, value in kwargs.items():
    #         if hasattr(value, '__iter__') and not isinstance(value, str):
    #                 # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
    #                 value = value[0]
    #         setattr(self, property, value)

    # def __repr__(self):
    #     return str(self.username)

class DetectTime(db.Model):
    __tablename__ = 'DetectTime'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(255), unique=False, nullable=False)
    time = db.Column(db.String(255), unique=False, nullable=False)
    action = db.Column(db.String(255), unique=False, nullable=True)
    image = db.Column(Text, unique=False, nullable=True)