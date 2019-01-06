# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64)
                                             ])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我的密码')
    submit = SubmitField('登陆')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码必须一致.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被使用')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须一致')])
    password2 = PasswordField('确认密码',
                              validators=[DataRequired()])
    submit = SubmitField('更改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('更改密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更新邮件信息')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被使用！')
