from flask import Flask, render_template, request, redirect, url_for, flash, json, make_response, session

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

from config import DevelopmentConfig

from helper import date_format

from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField, TextField, TextAreaField, SubmitField, FieldList, FormField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms import HiddenField
from wtforms import validators 
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)


#*****INICIO MODELO

class User(db.Model):    
    __tablename__ = 'users' #para asiganar un nombre de la tabla diferente, ya que por defecto asume como nombre el que lleva la clase
    id = db.Column(db.Integer, primary_key=True)
    coments = db.relationship('Coment')
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(80))
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

class Coment(db.Model):
    __tablename__ = 'coments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text())
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)

#****FIN MODELO****

#**** FORMS

def validacion_length(form, field):
    if len(field.data) > 0:
        raise validators.ValidationError('el campo debe estar vacio')

class formulario_registro(Form):
    username = TextField('Nombre',[validators.length(min = 4, max=15, message='ingrese un nombre valido')]) 
    email = EmailField('Email',[validators.Email(message='Ingrese un email valido')])
    password = PasswordField('Password',[validators.length(min = 4, max=15, message='ingrese un pasw valido')])

    def validate_username(form, field):#esto es override, ya que la funcion se crea automatica cuando se crean los campos
      username = field.data
      user = User.query.filter_by(username = username).first()
      if user:
        raise validators.ValidationError('Este username ya se encuentra registrado en la base de datos')

    def validate_email(form, field):#esto es override, ya que la funcion se crea automatica cuando se crean los campos
      email = field.data
      mail= User.query.filter_by(email = email).first()
      if mail:
        raise validators.ValidationError('Este email ya se encuentra registrado en la base de datos')
    
    
class formulario_login(Form):
    username = TextField('Nombre',[validators.length(min = 4, max=15, message='ingrese un nombre valido')])
    password = PasswordField('Password',[validators.length(min = 4, max=15, message='ingrese un pasw valido')])

class formulario_coment(Form):
    coment = TextAreaField('Comentario',[validators.length(min = 4, max=150, message='ingrese un comentario valido')])

#******FIN


@app.before_request #esto se ejcuta antes de "/", por ejemplo aca chequeamos si el usuario se ha chequeado
def before_request():
    if 'username' not in session and request.endpoint in ['inicio','coment','reviews'] :
        return redirect(url_for('login'))
    elif 'username' in session and request.endpoint in ['login','nuevo_registro']:
        return redirect(url_for('inicio'))

@app.after_request
def after_request(response):
    return response

@app.route("/")
def inicio():
    username = session['username']  # se asigna a una variable la session
    print('variable de session: ',username) #se imprime en el terminal
    return render_template('inicio.html', titulo = "Inicio",user = username)

@app.route("/nuevo_registro", methods=[ 'GET' ,'POST'])
def nuevo_registro():
    form = formulario_registro(request.form)
    if request.method == 'POST' and form.validate():
        pasw = generate_password_hash(password=request.form["password"], method='sha256')
        user = User(username=request.form["username"], email=request.form["email"], password =pasw)
        db.session.add(user)
        db.session.commit()
        success_message = 'Usuario creado existosamente'   
        flash(success_message)
    else:
        print(form.errors)
        print(form.username.errors)
    return render_template('form_registro.html', form = form)

@app.route("/login", methods=[ 'GET' ,'POST'])
def login():
    form = formulario_login(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username = username).first()
        if user and user.verify_password(password):
            session['username'] = username
            session['user_id']  = user.id #se toma el id del username y se crea la session, esto se hixo para poder registrar los comentarios posteriomente
            success_message = 'Bienvenido al sistema, {}'.format(username) 
            flash(success_message)
            return redirect(url_for('inicio'))        
        else:
            error_message = 'Usuario o contraseña no valida'
            flash(error_message)
    return render_template('login.html', form = form)

@app.route("/coment", methods=[ 'GET' ,'POST'])
def coment():
    form = formulario_coment(request.form)
    user_id = session['user_id']
    username = session['username']
    if request.method == 'POST' and form.validate():
        coment = Coment(user_id = user_id,text = form.coment.data)
        db.session.add(coment)
        db.session.commit()
        success_message = 'Comentario creado existosamente'   
        flash(success_message)
    return render_template('coment.html', form = form, user = username)

@app.route("/reviews/", methods=[ 'GET' ])
@app.route("/reviews/<int:pagina>", methods=[ 'GET' ])
def reviews(pagina=1):
    usuario = session['username']
    #conecto las tablas Coment y User utilizando join, la cual es posible ya que en el modelo ya esta definida la relacion entre las 2 tablas mediante el id
    Coment_list = Coment.query.join(User).add_columns(User.username, Coment.text, Coment.created_date).paginate(pagina,4,False)
    return render_template('reviews.html', coments =  Coment_list, date_format = date_format, user = usuario)

@app.route('/logout')
def logout():  
    username_sesion = session['username']
    if 'username' in session:   #se chequea si username esta dentro del dicionario de session
        session.pop('username') #elimina la session  
        session.pop('user_id')
        print ('Salida del sistema por: '+username_sesion)
    return redirect(url_for("login"))


@app.errorhandler(404)
def error_404(e):
    return render_template('error_404.html'), 404


if __name__ == '__main__':
    db.create_all()
    app.run()

    
    
    



    
