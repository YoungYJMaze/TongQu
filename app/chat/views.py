# -*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, \
            current_user
from . import chat
from .. import db
from ..__init__ import socketio
from flask_socketio import emit
from ..decorators import admin_required, permission_required
from ..models import Permission, Role, User, Post, Comment, Message
from ..email import send_email
from bleach import clean, linkify
from flask import flash
from markdown import markdown

import functools
from flask import request
from flask_login import current_user
from flask_socketio import disconnect
from sqlalchemy import and_
from sqlalchemy import or_
online_users=[]


def to_html(raw):
    allowed_tags = ['a', 'abbr', 'b', 'br', 'blockquote', 'code',
                    'del', 'div', 'em', 'img', 'p', 'pre', 'strong',
                    'span', 'ul', 'li', 'ol']
    allowed_attributes = ['src', 'title', 'alt', 'href', 'class']
    html = markdown(raw, output_format='html',
                    extensions=['markdown.extensions.fenced_code',
                                'markdown.extensions.codehilite'])
    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)
    return linkify(clean_html)

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
                        return f(*args, **kwargs)
    return wrapped



@socketio.on('my event')
@authenticated_only
def handle_my_custom_event(data):
    emit('my response', {'message': '{0} has joined'.format(current_user.name)},
                     broadcast=True)


@socketio.on('new message',namespace='/room')
def new_message(message_body):
    html_message = to_html(message_body)
    message = Message(author=current_user._get_current_object(), body=html_message,to='room')
    db.session.add(message)
    db.session.commit()
    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message),
          'message_body': html_message,
          'gravatar': current_user.gravatar(),
          'nickname': current_user.username,
          'user_id': current_user.id},
         namespace='/room',
         broadcast=True,
         )

@socketio.on('new message',namespace='/friends')
def new_message(message_body):
    global to
    html_message = to_html(message_body)
    message = Message(author=current_user._get_current_object(), body=html_message, to=to)
    db.session.add(message)
    db.session.commit()
    emit('new message',
         {'message_html': render_template('chat/_message.html', message=message),
          'message_body': html_message,
          'gravatar': current_user.gravatar(),
          'nickname': current_user.username,
          'user_id': current_user.id},
         namespace='/friends',
         broadcast=True,
         )

@socketio.on('connect')
def connect():
    global online_users
    if current_user.is_authenticated and current_user not in online_users:
        online_users.append(current_user)
    emit('user count', {'count': len(online_users)}, broadcast=True)


@socketio.on('disconnect')
def disconnect():
    global online_users
    if current_user.is_authenticated and current_user in online_users:
        online_users.remove(current_user)
    emit('user count', {'count': len(online_users)}, broadcast=True)


@chat.route('/room')
@login_required
def room():
    global online_users
    amount = current_app.config['FLASKY_POSTS_PER_PAGE']
    messages = Message.query.filter(Message.to=='room').order_by(Message.timestamp.asc())[-amount:]
    user_amount = User.query.count()
    online_num=len(online_users)
    token=current_user.generate_auth_token(3600)
    return render_template('chat/room.html',messages=messages, user_amount=user_amount,online_user=online_num,token=token,users=online_users)


@chat.route('/friends')
@login_required
def friends():
    global to
    to=''
    user=current_user
    token=current_user.generate_auth_token(3600)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]

    return render_template('chat/friends.html',token=token,follows=follows)

@chat.route('/friends/<othername>')
@login_required
def friend(othername):
    global to
    to=othername
    user=current_user
    token=current_user.generate_auth_token(3600)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    other=User.query.filter(User.username==othername).first()
    othername_id=other.id
    messages = Message.query.filter(and_(Message.to==othername,Message.author_id==current_user.id))
    messages1 = Message.query.filter(and_(Message.to==current_user.username,Message.author_id==othername_id))
    messages=messages.union(messages1).order_by(Message.timestamp.asc())

    return render_template('chat/friends.html',messages=messages,token=token,follows=follows,othername=othername,to=to)


@chat.route('/messages')
def get_messages():
    page = request.args.get('page', 1,type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'])
    messages = pagination.items
    return render_template('chat/_messages.html', messages=messages[::-1])

@chat.route('/user/<user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('chat/_profile_card.html', user=user)



@chat.route('/message/delete/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if current_user != message.author and not current_user.is_admin:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    return '', 204
