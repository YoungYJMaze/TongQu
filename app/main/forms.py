# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, FileField, SelectMultipleField, FloatField, RadioField,Label
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField('您的用户名', validators=[DataRequired()])
    submit = SubmitField('提交')


class EditProfileForm(FlaskForm):
    avatar = FileField('头像')
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('您的位置', validators=[Length(0, 64)])
    about_me = TextAreaField('个人介绍')

    study = BooleanField('学习')
    games = BooleanField('游戏')
    sports = BooleanField('运动')
    music =BooleanField('音乐')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '用户名必须至少包含字母和数字')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    avatar = FileField('头像')
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('您的位置', validators=[Length(0, 64)])
    about_me = TextAreaField('个人介绍')
    study = BooleanField('学习')
    games = BooleanField('游戏')
    sports = BooleanField('运动')
    music =BooleanField('音乐')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('验证邮件已发送至您的邮箱')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')


class PostForm(FlaskForm):
    body = PageDownField("说点儿什么吧", validators=[DataRequired()])
    sort = StringField("分类:",validators=[DataRequired()],id='sortform')
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = StringField('',validators=[DataRequired()])
    submit = SubmitField('提交')

class SortForm(FlaskForm):
    select = StringField('按兴趣查看:',validators=[DataRequired()])
    enter = SubmitField('确定')


