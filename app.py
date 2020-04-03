from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from time import time
from random import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'frida'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://javi:javiersolis12@localhost:3306/Tuti'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class configuracion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.Integer)
    frec = db.Column(db.Integer)

class tecnicos(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombres = db.Column(db.String(80))
    apellidos = db.Column(db.String(80))
    email = db.Column(db.String(80))
    celular = db.Column(db.String(80))

class todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    temperatura = db.Column(db.Float())
    humedad = db.Column(db.Float())
    canal1 = db.Column(db.Float())
    canal2 = db.Column(db.Float())
    canal3 = db.Column(db.Float())
    canal4 = db.Column(db.Float())
    hora = db.Column(db.Time())
    fecha = db.Column(db.Date())

class ahora(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    temperatura = db.Column(db.Float(10))
    humedad = db.Column(db.Float(10))
    canal1 = db.Column(db.Float(10))
    canal2 = db.Column(db.Float(10))
    canal3 = db.Column(db.Float(10))
    canal4 = db.Column(db.Float(10))
    hora = db.Column(db.Time())


@app.route('/')
def home():
    sensores = ahora.query.filter_by(id=1).first()
    return render_template('index.html', titulo='DASHBOARD TUTI', graph = sensores)


@app.route('/vtecnicos')
def VistaTecnicos():
    return render_template('vtecnicos.html', titulo='Registro de Técnicos')


@app.route('/rtecnicos', methods=['POST'])
def RegistroTecnicos():
    if request.method == 'POST':
        nuevoTecnico = tecnicos(
            nombre = request.form['nombre'],
            apellido = request.form['apellido'],
            email = request.form['email'],
            telf = request.form['celular'])
        db.session.add(nuevoTecnico)
        db.session.commit()
        return redirect(url_for('VistaTecnicos'))

@app.route('/sensores')
def prueba():
    sensores = ahora.query.filter_by(id=1).first()
    json_data = sensores
    return jsonify({'temperatura' : sensores.temperatura,
                    'humedad' : sensores.humedad,
                    'canal1' : sensores.canal1,
                    'canal2' : sensores.canal2,
                    'canal3' : sensores.canal3,
                    'canal4' : sensores.canal4})

@app.route('/datos', methods=["GET", "POST"])
def data1():
    sensores = ahora.query.filter_by(id=1).first()
    data = [(time() - 14400) * 1000, sensores.temperatura, sensores.humedad, round(sensores.canal1,4), round(sensores.canal2,4), round(sensores.canal3,4), round(sensores.canal4,4)]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/data', methods=["GET", "POST"])
def data():
    # Data Format
    # [TIME, Temperature, Humidity]
    Temperature = random() * 100
    Humidity = random() * 55
    data = [time() * 1000, Temperature, Humidity]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
