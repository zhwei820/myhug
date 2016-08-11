# -*- coding: utf-8 -*-
import time

from flask import Flask
from flask import request, url_for, redirect, abort, render_template_string

from flask_sqlalchemy import SQLAlchemy
from rc import Cache

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
db = SQLAlchemy(app)
cache = Cache()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_ts = db.Column(db.Integer, nullable=False)
    updated_ts = db.Column(db.Integer, nullable=False)

    def __init__(self, title, content, created_ts, updated_ts):
        self.title = title
        self.content = content
        self.created_ts = created_ts
        self.updated_ts = updated_ts

    def __repr__(self):
        return '<Post %s>' % self.id

    @staticmethod
    def add(title, content):
        current_ts = int(time.time())
        post = Post(title, content, current_ts, current_ts)
        db.session.add(post)
        db.session.commit()
        cache.invalidate(Post.get_by_id, post.id)
        cache.invalidate(Post.get_all_ids)

    @staticmethod
    def update(post_id, title, content):
        post = Post.query.get(post_id)
        post.title = title
        post.content = content
        post.updated_ts = int(time.time())
        db.session.commit()
        cache.invalidate(Post.get_by_id, post.id)

    @staticmethod
    @cache.cache()
    def get_all_ids():
        posts = Post.query.all()
        return [post.id for post in posts]

    @staticmethod
    @cache.cache()
    def get_by_id(post_id):
        post = Post.query.get(post_id)
        return dict(id=post.id, title=post.title, content=post.content,
                    created_ts=post.created_ts, updated_ts=post.updated_ts)
