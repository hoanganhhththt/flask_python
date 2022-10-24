from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Float, Integer
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message

db = SQLAlchemy()
app = Flask(__name__)
ma= Marshmallow(app)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret' #change this IRL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'hoanganh@gmail.com'
app.config['MAIL_PASSWORD'] = '09081999'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db.init_app(app)
jwt = JWTManager(app)
mail = Mail(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('DB created!!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('DB dropped!!')

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury', planet_type='Class D', home_star='Sol', mass=3.258e23, radius=1516, distance=35.98e6)
    venus = Planet(planet_name='Venus', planet_type='Class K', home_star='Sol', mass=3.258e23, radius=3760, distance=35.98e6)
    earth = Planet(planet_name='Earth', planet_type='Class M', home_star='Sol', mass=3.258e23, radius=3760, distance=35.98e6)
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='Hoang', last_name='Anh', email='test@gamil.com', password='09081999')
    db.session.add(test_user)
    db.session.commit()
    print('DB seed!!!')

@app.route('/')
def hello_world():
    return 'Hello haha'

@app.route('/test')
def test_api():
    return jsonify(message='OKOKOK', code= '01'), 200

@app.route('/not-found')
def not_found():
    return jsonify(message='not found'), 404

@app.route('/parameters')
def test_params():
    name = request.args.get('name')
    age = int(request.args.get('age'))

    if(age < 18):
        return jsonify(message='You are not enough 18'), 401
    else:
        return jsonify(message=name + ' OK'), 200


@app.route('/params_url/<string:name>/<int:age>')
def test_params_url(name:str, age:int):
    if(age < 18):
        return jsonify(message='You are not enough 18'), 401
    else:
        return jsonify(message=name + ' OK'), 200


@app.route('/get-all-planets', methods=['GET'])
def get_all_planets():
    list_planets = Planet.query.all()
    result = planets_schema.dump(list_planets)
    return jsonify(data=result)

@app.route('/register-user', methods=['POST'])
def register_user():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email already exists'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='Created user success'), 201

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login success', access_token=access_token)
    else:
        return jsonify(message='Bad email or password'), 401

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    if request.is_json:
        email = request.json['email']
    else:
        email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        msg = Message('Your new password is' + test.password, sender="anh.lh182337@gmail.com", recipients=[email])
        mail.send(msg)
        return jsonify(message='Password send to' + email)
    else:
        return jsonify(message='The bad email')


@app.route('/reset-password/<string:email>', methods=['GET'])
def get_password(email: str):
    test = User.query.filter_by(email=email).first()
    if test:
        msg = Message('Your new password is' + test.password, sender="anh.lh182337@gmail.com", recipients=[email])
        mail.send(msg)
        return jsonify(message='Password send to' + email)
    else:
        return jsonify(message='The bad email')



# database models

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key = True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)


app.run()