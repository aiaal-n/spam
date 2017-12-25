import builtins
import socket
#import names

import smtplib
from flask_paginate import Pagination, get_page_parameter
import os
import pyexcel

from flask import render_template, request, redirect, url_for, flash, session, jsonify, json, Response

from app import app
from app.models import Mails, db, TemplateMessage, User, Groups
from sqlalchemy import update

from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from validate_email import validate_email

app.secret_key = '_\x1ea\xc2>DK\x13\xd0O\xbe1\x13\x1b\x93h2*\x9a+!?\xcb\x8f'

group = -1


@app.route('/', methods=["POST", "GET"])
def index():
    global group
    if request.method == 'POST':
        name = request.form.get('groups')
        groups = Groups.query.all()
        page_id = request.args.get('id')
        if page_id is None:
            ITEMS_PER_PAGE = 10
        else:
            ITEMS_PER_PAGE = int(page_id)
        group = name
        if int(name) == -1:
            group = name
            template_message = TemplateMessage.query.all()
            data_len = Mails.query.all()
            data = Mails.query.paginate(1, ITEMS_PER_PAGE, error_out=False).items
            pagination = Pagination(page=1, total=len(data_len), format_total=len(data), format_number=True,
                                    per_page=ITEMS_PER_PAGE,
                                    css_framework='bootstrap3', active_url='users-page-url', record_name='data')

            return render_template("index.html", page=1, template=template_message, per_page=ITEMS_PER_PAGE,
                                   data=data,
                                   pagination=pagination, groups=groups)
        template_message = TemplateMessage.query.all()
        data_len = Mails.query.filter_by(group_id=name).all()
        data = Mails.query.filter_by(group_id=name).paginate(1, ITEMS_PER_PAGE, error_out=False).items
        if data:
            pagination = Pagination(page=1, total=len(data_len), format_total=len(data), format_number=True,
                                    per_page=ITEMS_PER_PAGE,
                                    css_framework='bootstrap3', active_url='users-page-url', record_name='data')

            return render_template("index.html", page=1, template=template_message, per_page=ITEMS_PER_PAGE, data=data,
                                   pagination=pagination, groups=groups)
        else:
            group = -1
            pagination = Pagination(page=1, total=len(data_len), format_total=len(data), format_number=True,
                                    per_page=ITEMS_PER_PAGE,
                                    css_framework='bootstrap3', active_url='users-page-url', record_name='data')

            return render_template("index.html", page=1, template=template_message, per_page=ITEMS_PER_PAGE, data=data,
                                   pagination=pagination, groups=groups)
    if int(group) == -1:
        groups = Groups.query.all()
        page_id = request.args.get('id')
        if page_id is None:
            ITEMS_PER_PAGE = 10
        else:
            ITEMS_PER_PAGE = int(page_id)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        template_message = TemplateMessage.query.all()
        data_len = Mails.query.all()
        data = Mails.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
        pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                                per_page=ITEMS_PER_PAGE,
                                css_framework='bootstrap3', active_url='users-page-url', record_name='data')

        return render_template("index.html", page=page, template=template_message, per_page=ITEMS_PER_PAGE,
                               data=data,
                               pagination=pagination, groups=groups)
    else:
        groups = Groups.query.all()
        page_id = request.args.get('id')
        if page_id is None:
            ITEMS_PER_PAGE = 10
        else:
            ITEMS_PER_PAGE = int(page_id)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        template_message = TemplateMessage.query.all()
        data_len = Mails.query.filter_by(group_id=group).all()
        data = Mails.query.filter_by(group_id=group).paginate(page, ITEMS_PER_PAGE, error_out=False).items
        pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                                per_page=ITEMS_PER_PAGE,
                                css_framework='bootstrap3', active_url='users-page-url', record_name='data')

        return render_template("index.html", page=page, template=template_message, per_page=ITEMS_PER_PAGE, data=data,
                               pagination=pagination, groups=groups)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            if loginSite is None:
                flash("Неправильно введен логин")
                return redirect(url_for('login'))
            else:
                if loginSite.check_password(password):
                    session['email'] = loginSite.email
                    session['port'] = loginSite.port
                    session['host'] = loginSite.host
                    session['id'] = loginSite.id
                    return redirect('/')
                else:
                    flash("Неправильно введен пароль")
                    return redirect(url_for('login'))
        else:
            flash("Неправильно введена почта")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        host = request.form['host']
        port = request.form['port']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            flash("Логин занят")
            return redirect(url_for('register'))
        else:
            if password == cpassword:
                user = User(email=email, host=host, port=port, password=password, cpassword=cpassword)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))
            else:
                flash("Пароли не совпадают!")
                return redirect(url_for('register'))

    return render_template('registration.html')


@app.route("/profile", methods=['POST', 'GET'])
def profile():
    data = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        host = request.form['host']
        port = request.form['port']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        if password == cpassword:
            message = update(User).where(User.email == session['email']).values(email=email, host=host, port=port,
                                                                                cpassword=cpassword)
            db.session.execute(message)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("Пароли не совпадают!")
            return redirect(url_for('profile'))
    return render_template('profile.html', data=data)


@app.route('/logout')
def logout():
    # удалить из сессии имя пользователя, если оно там есть
    session.pop('email', None)
    return redirect('/')


@app.route("/dowload", methods=["POST", "GET"])
def dowload():
    groups = Groups.query.all()
    if request.method == "POST":
        columnNameOrg = request.form['column1']
        columnEmail = request.form['column2']
        groups = request.form['groups']
        file = request.files['inputFile'].read()
        if not file:
            return "No file"
        sheet = pyexcel.get_sheet(file_type="xlsx", file_content=file)
        for column in sheet.row:
            try:
                if validate_email(column[int(columnEmail) - 1]):
                    addMail = Mails(name=column[int(columnNameOrg) - 1], mails=column[int(columnEmail) - 1],
                                    group_id=groups)
                    db.session.add(addMail)
                    db.session.commit()
            # except builtins.TypeError:
            #     flash('Выбрана не правильная колонна')
            #     return redirect(url_for('dowload'))
            except builtins.IndexError:
                flash('Выбрана не правильная колонна')
                return redirect(url_for('dowload'))
        return redirect(url_for('index'))
    return render_template("dowloads.html", groups=groups)


@app.route("/send", methods=["POST", "GET"])
def send():
    if request.method == "POST":
        list_id = request.form.get('list_id', "").split(",")
        message_id = request.form.get('template')
        message = TemplateMessage.query.filter_by(id=message_id).first()
        for i in list_id:
            data = Mails.query.filter_by(id=i).first()
            try:
                send_message(data.mails, message.name, message.message, message.file)
            except builtins.AttributeError:
                flash("Шаблон сообщения не выбран")
                return redirect("/")
    return redirect(url_for('index'))


@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        list_id = request.form.get('list_id_del', "").split(",")
        for id_org in list_id:
            if id_org != "":
                ses1 = Mails.query.filter_by(id=id_org).all()
                for s in ses1:
                    db.session.delete(s)
                    db.session.commit()
    return redirect(url_for('index'))


@app.route("/create", methods=["POST", "GET"])
def create():
    groups = Groups.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        groups = request.form.get('groups')
        message = Mails(name=name, mails=email, group_id=groups)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', groups=groups)


@app.route("/update/", methods=["POST", "GET"])
def update_org():
    groups = Groups.query.all()
    id = request.args.get('id')
    if id is None:
        return '', 404
    data = Mails.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        groups = request.form.get('groups')
        message = update(Mails).where(Mails.id == id).values(name=name, mails=email, group_id=groups)
        db.session.execute(message)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', data=data, groups=groups)


@app.route("/template", methods=["GET"])
def template():
    page_id = request.args.get('id')
    if page_id is None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(page_id)
    data_len = TemplateMessage.query.all()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    data = TemplateMessage.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                            per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("template.html", page=page, per_page=ITEMS_PER_PAGE, data=data, pagination=pagination)


@app.route("/template/create", methods=["POST", "GET"])
def template_create():
    if request.method == 'POST':
        name = request.form.get('name')
        mess = request.form.get('message')
        file = request.files['inputFile']
        if file.filename == '':
            filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = TemplateMessage(name=name, message=mess, file=filename)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('template'))
    return render_template('templateCreate.html')


@app.route("/template/update/", methods=["POST", "GET"])
def template_update():
    id = request.args.get('id')
    if id is None:
        return '', 404
    data = TemplateMessage.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        mess = request.form.get('message')
        file = request.files['inputFile']
        if file.filename == '':
            if data.file != '':
                filename = data.file
            else:
                filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = update(TemplateMessage).where(TemplateMessage.id == id).values(name=name, message=mess, file=filename)
        db.session.execute(message)
        db.session.commit()
        return redirect(url_for('template'))
    return render_template('templateUpdate.html', data=data)


@app.route("/template/delete/", methods=["POST", "GET"])
def template_delete():
    id = request.args.get('id')
    if id is None:
        return '', 404
    a = TemplateMessage.query.filter_by(id=id).first()
    if a.file != '':
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], a.file))
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('template'))


@app.route("/groups", methods=["POST", "GET"])
def groups():
    page_id = request.args.get('id')
    if page_id is None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(page_id)
    data_len = Groups.query.all()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    data = Groups.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                            per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("groups.html", page=page, per_page=ITEMS_PER_PAGE, data=data, pagination=pagination)


@app.route("/groups/create", methods=["POST", "GET"])
def groups_create():
    if request.method == 'POST':
        name = request.form.get('name')
        message = Groups(name=name)
        db.session.add(message)
        db.session.commit()
        return redirect('/groups')
    return render_template('groupsCreate.html')


@app.route("/groups/update/", methods=["POST", "GET"])
def groups_update():
    id = request.args.get('id')
    if id is None:
        return '', 404
    data = Groups.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        message = update(Groups).where(Groups.id == id).values(name=name)
        db.session.execute(message)
        db.session.commit()
        return redirect('/groups')
    return render_template('groupsUpdate.html', data=data)


@app.route("/groups/delete/", methods=["POST", "GET"])
def groups_delete():
    id = request.args.get('id')
    if id is None:
        return '', 404
    a = Groups.query.filter_by(id=id).first()
    db.session.delete(a)
    db.session.commit()
    return redirect('/groups')


def send_message(email, subject, message, files):
    if 'email' in session:
        loginSite = User.query.filter_by(email=session['email']).first()
        if not loginSite:
            flash('Вход не выполнен')
            return url_for('index')
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = loginSite.email
        msg['To'] = email
        msg.preamble = """
        Your mail reader does not support the report format.
        Please visit us <a href="http://www.mysite.com">online</a>!"""

        HTML_TEXT = MIMEText(message, 'html')
        msg.attach(HTML_TEXT)

        if files != '':
            path = os.path.join(app.config['UPLOAD_FOLDER'], files)
            with open(path, 'rb') as fp:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(fp.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=files)
            msg.attach(part)
        try:
            s = smtplib.SMTP(host=loginSite.host, port=loginSite.port)  # mail.nic.ru
        except smtplib.SMTPServerDisconnected:
            flash('Сервер недоступен')
            return url_for('index')
        except builtins.TimeoutError:
            flash('Не правильно введен порт')
            return url_for('index')
        except socket.gaierror:
            flash('Не правильно введен хост')
            return url_for('index')
        s.ehlo()
        s.starttls()
        s.ehlo()
        try:
            s.login(loginSite.email, loginSite.cpassword)
        except smtplib.SMTPAuthenticationError:
            flash("Не правильно введена почта или пароль.")
            return url_for('index')
        print(email)
        try:
            s.sendmail(loginSite.email, email, msg.as_string())
        except builtins.UnicodeEncodeError:
            flash("Неправильно введена электронная почта " + email)
            return url_for('index')
        s.quit()
    else:
        flash('Вход не выполнен')
        return url_for('index')


def obj_dict(obj):
    return obj.__dict__


@app.route("/api/init", methods=["POST", "GET"])
def api_init():
    if request.method == 'POST':
        data = request.get_json()
        # dataDict = json.loads(data)
        id = data['id']
        loginSite = User.query.filter_by(id=id).first()
        if loginSite:
            groups = Groups.query.all()
            templates = TemplateMessage.query.all()
            return jsonify({'auth':True, 'groups':[dict(id=g.id, name=g.name) for g in groups], 'templates':[dict(id=t.id, name=t.name, message=t.message) for t in templates]})
        else:
            return jsonify({'auth':False})
        # return jsonify({'mails':data['msg']})
    # json.dumps([u.as_dict() for u in Mails.query.filter_by(mails="mosolov06@mail.ru").all()])
    # results = [ob.as_json() for ob in resultset]
    # list=[]
    # list = [u.__dict__ for u in Mails.query.filter_by(mails="mosolov06@mail.ru").all()]
    groups = Groups.query.all()
    templates = TemplateMessage.query.all()
    return jsonify({'auth': True, 'groups': [dict(id=g.id, name=g.name) for g in groups],
                    'templates': [dict(id=t.id, name=t.name, message=t.message) for t in templates]})
    # return json.dumps(Mails.query.filter_by(mails="mosolov06@mail.ru").all(), default=obj_dict)
# Response(json.dumps([u.as_dict() for u in Mails.query.filter_by(mails="mosolov06@mail.ru").all()]))
# jsonify({'mails':"s"})


@app.route("/api/login", methods=["POST", "GET"])
def api_login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['pass']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            if loginSite is None:
                return jsonify({'msg':"error"})
            else:
                if loginSite.check_password(password):
                    return jsonify({'msg':"success", 'id':loginSite.id})
                else:
                    return jsonify({'msg':"error"})
        else:
            return jsonify({'msg':"error"})


@app.route("/api/list", methods=["POST", "GET"])
def api_list():
    # arr = []
    # list = Mails.query.filter_by(group_id="3").all()
    # for l in list:
    #     arr.append(l.mails)
    a = jsonify({"items":[dict(id=u.id, mails=u.mails, name=u.name, group_id=u.group_id) for u in Mails.query.filter_by(group_id="3").all()]})
    return a
    # json.dumps([u.as_dict() for u in Mails.query.filter_by(mails="DalurMO@yandex.ru").all()])
    # results = [ob.as_json() for ob in resultset]
    # list=[]
    # list = [u.__dict__ for u in Mails.query.filter_by(mails="mosolov06@mail.ru").all()]


@app.route("/api/register", methods=["POST", "GET"])
def api_register():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        host = data['host']
        port = data['port']
        password = data['pass']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            return jsonify({'msg':"error"})
        else:
            user = User(email=email, host=host, port=port, password=password, cpassword=password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'msg':"success"})


@app.route("/api/add-email", methods=["POST", "GET"])
def api_add_email():
    if request.method == "POST":
        data = request.get_json()
        email = data['email']
        name = data['name']
        groups = data['group_id']
        message = Mails(name=name, mails=email, group_id=groups)
        db.session.add(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/edit-email", methods=["POST", "GET"])
def api_edit_email():
    if request.method == "POST":
        data = request.get_json()
        id = data['id']
        email = data['email']
        name = data['name']
        groups = data['groups']
        message = update(Mails).where(Mails.id == id).values(name=name, mails=email, group_id=groups)
        db.session.execute(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/del-email", methods=["POST", "GET"])
def api_del_email():
    if request.method == "POST":
        data = request.get_json()
        list_id = data['ids']
        for id_org in list_id:
            if id_org != "":
                ses1 = Mails.query.filter_by(id=id_org).all()
                for s in ses1:
                    db.session.delete(s)
                    db.session.commit()
                    return jsonify({'msg': "success"})
        return jsonify({'msg': "false"})


@app.route("/api/add-group", methods=["POST"])
def api_add_group():
    if request.method == "POST":
        data = request.get_json()
        name = data['name']
        message = Groups(name=name)
        db.session.add(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/edit-group", methods=["POST"])
def api_edit_group():
    if request.method == "POST":
        data = request.get_json()
        id = data['id']
        name = data['name']
        message = update(Groups).where(Groups.id == id).values(name=name)
        db.session.execute(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/del-group", methods=["POST"])
def api_del_group():
    if request.method == "POST":
        data = request.get_json()
        id = data['id']
        a = Groups.query.filter_by(id=id).first()
        db.session.delete(a)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/add-template", methods=["POST"])
def api_add_template():
    if request.method == "POST":
        data = request.get_json()
        name = data['name']
        mess = data['message']
        file = request.files['inputFile']
        if file.filename == '':
            filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = TemplateMessage(name=name, message=mess, file=filename)
        db.session.add(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/edit-template", methods=["POST"])
def api_edit_template():
    if request.method == "POST":
        data = request.get_json()
        id = data['id']
        name = data['name']
        mess = data['message']
        file = request.files['inputFile']
        if file.filename == '':
            if data.file != '':
                filename = data.file
            else:
                filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = update(TemplateMessage).where(TemplateMessage.id == id).values(name=name, message=mess, file=filename)
        db.session.execute(message)
        db.session.commit()
        return jsonify({'msg': "success"})


@app.route("/api/del-template", methods=["POST"])
def api_del_template():
    if request.method == "POST":
        data = request.get_json()
        id = data['id']
        a = TemplateMessage.query.filter_by(id=id).first()
        if a.file != '':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], a.file))
        db.session.delete(a)
        db.session.commit()
        return jsonify({'msg': "success"})