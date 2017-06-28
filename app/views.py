from flask import json
import smtplib, re
import random, json
import pyexcel.ext.xls
from flask_paginate import Pagination, get_page_parameter
import os

from flask import render_template, request, session, redirect, flash, url_for

from app import app
from datetime import datetime
from app.models import Mails, db, TemplateMessage
from sqlalchemy import update


from email.header import Header
from email.mime.text import MIMEText
from validate_email import validate_email

app.secret_key = '_\x1ea\xc2>DK\x13\xd0O\xbe1\x13\x1b\x93h2*\x9a+!?\xcb\x8f'


# ITEMS_PER_PAGE = 10

@app.route('/', methods=["POST", "GET"])
def index():
    id = request.args.get('id')
    if id == None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(id)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    template = TemplateMessage.query.all()
    data_len = Mails.query.all()
    data = Mails.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True, per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("index.html", page=page, template=template, per_page=ITEMS_PER_PAGE, data=data, pagination=pagination)


@app.route("/dowload", methods=["POST", "GET"])
def dowload():
    if request.method == "POST":
        file = request.files['inputFile'].read()
        if not file:
            return "No file"
        sheet = pyexcel.get_sheet(file_type="xlsx", file_content=file)
        for column in sheet.row:
            if validate_email(column[2]):
                addMail = Mails(name=column[1], mails=column[2])
                db.session.add(addMail)
                db.session.commit()
        return render_template("dowloads.html", message='Успешно загружено')
    return render_template("dowloads.html")


@app.route("/send", methods=["POST", "GET"])
def send():
    if request.method == "POST":
        list_id = request.form.get('list_id', "").split(",")
        message_id = request.form.get('template')
        print(message_id)
        # message = TemplateMessage.query.filter_by(id=message_id).first()
        # print(message.message)
        for i in list_id:
            data = Mails.query.filter_by(id=i).first()
            print(data.mails)
    return redirect(url_for('index'))


@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        list_id = request.form.get('list_id_del', "").split(",")
        for id_org in list_id:
            ses1 = Mails.query.filter_by(id=id_org).all()
            for s in ses1:
                db.session.delete(s)
                db.session.commit()
    return redirect(url_for('index'))


@app.route("/template", methods=["GET"])
def template():
    id = request.args.get('id')
    if id == None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(id)
    data_len = TemplateMessage.query.all()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    data = TemplateMessage.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True, per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("template.html", page=page, per_page=ITEMS_PER_PAGE, data=data, pagination=pagination)


@app.route("/template/create", methods=["POST", "GET"])
def templateCreate():
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
def templateUpdate():
    id = request.args.get('id')
    if id is None:
        return '', 404
    data = TemplateMessage.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        mess = request.form.get('message')
        file = request.files['inputFile']
        if file.filename == '':
            if (data.file != ''):
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
def templateDelete():
    id = request.args.get('id')
    if id is None:
        return '', 404
    a = TemplateMessage.query.filter_by(id=id).first()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], a.file))
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('template'))


def sendMessage(email, message):
    with open('data.json') as data_file:
        data = json.load(data_file)
    msg = MIMEText(message, 'plain', 'utf-8')
    thread_number = random.randint(0, 10000)
    msg['Subject'] = Header('Minutely Spam Report (randomizer: ' + str(thread_number) + ')', 'utf-8')
    msg['From'] = data['email']
    msg['To'] = ', '.join(email)

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(data['email'], data['password'])
    s.sendmail(data['email'], email, msg.as_string())

    print("Email sent to: " + ', '.join(email))
    s.quit()
