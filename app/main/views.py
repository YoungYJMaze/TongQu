# -*- coding: UTF-8 -*-
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import Permission, Role, User, Post
from ..decorators import admin_required
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm,SortForm
from .. import db
from ..models import Permission, Role, User, Post, Comment
from ..decorators import admin_required, permission_required



@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    form1 = SortForm()
    if current_user.can(Permission.WRITE) and form.submit.data and form.validate_on_submit():
        post = Post(body=form.body.data,
            author=current_user._get_current_object(),sort=form.sort.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    if form1.enter.data and form1.validate_on_submit():
        page = request.args.get('page', 1 ,type=int)
        pagination = Post.query.filter(Post.sort.like(form1.select.data)).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
        posts = pagination.items
        return render_template('index.html', form=form,form1=form1, posts=posts,
                           pagination=pagination)
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
             error_out=False)
        posts = pagination.items
        return render_template('index.html', form=form,form1=form1, posts=posts,
                           pagination=pagination)

@main.route('/<cla>')
@login_required
def index_show(cla):
    form = PostForm()
    form1 = SortForm()
    if current_user.can(Permission.WRITE) and form.submit.data and form.validate_on_submit():
        post = Post(body=form.body.data,
            author=current_user._get_current_object(),sort=form.sort.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    if cla:
        page = request.args.get('page', 1 ,type=int)
        pagination = Post.query.filter(Post.sort.like(cla)).order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
        posts = pagination.items
        return render_template('index.html', form=form,form1=form1, posts=posts,
                           pagination=pagination)


@main.route('/show/<sortname>',methods=['GET','POST'])
@login_required
def show(sortname):
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.submit.data  and form.validate_on_submit():
        post = Post(body=form.body.data,
             author=current_user._get_current_object(),sort=form.sort.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
             )
    posts = pagination.items
    return render_template('index.html', form=[form,form1], posts=posts,
         pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():

        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        concern = []
        if form.games.data:
            concern.append(form.games.name)
        if form.sports.data:
            concern.append(form.sports.name)
        if form.study.data:
            concern.append(form.study.name)
        if form.music.data:
            concern.append(form.music.name)

        concernlist = " ".join(concern)
        current_user.concern = concernlist
        avatar = request.files['avatar']
        fname= avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS= ['png','jpg','jpeg','gif']
        flag = '.' in fname and fname.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('文件类型错误，必须是png，jpg，jpeg，gif格式中的一种')
            return redirect(url_for('.user',username=current_user.username))
        avatar.save(u'{}{}_{}'.format(UPLOAD_FOLDER,current_user.username,fname))
        current_user.real_avatar = u'/static/avatar/{}_{}'.format(current_user.username ,fname)
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('您的用户档案已更新.')
        return redirect(url_for('.user', username=current_user.username))
    form.avatar=current_user.real_avatar
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        concern = []
        if form.games.data:
            concern.append(form.games.name)
        if form.sports.data:
            concern.append(form.sports.name)
        if form.study.data:
            concern.append(form.study.name)
        if form.music.data:
            concern.append(form.music.name)

        concernlist = " ".join(concern)
        current_user.concern = concernlist
        avatar = request.files['avatar']
        fname= avatar.filename
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        ALLOWED_EXTENSIONS= ['png','jpg','jpeg','gif']
        flag = '.' in fname and fname.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            flash('文件类型错误，必须是png，jpg，jpeg，gif格式中的一种')
            return redirect(url_for('.user',username=current_user.username))
        avatar.save(u'{}{}_{}'.format(UPLOAD_FOLDER,current_user.username,fname))
        current_user.real_avatar = u'/static/avatar/{}_{}'.format(current_user.username ,fname)
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('用户档案已更新.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.avatar=current_user.real_avatar
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('发布成功.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.sort = form.sort.data
        db.session.add(post)
        db.session.commit()
        flash('已更新.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    form.sort.data = post.sort
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了这个用户。')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('你现在已经关注了 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你还没有关注这个用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('你已经不再关注 %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="被关注信息：",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="关注信息：",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


