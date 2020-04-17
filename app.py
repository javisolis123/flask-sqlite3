from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from time import time
from random import random
import json
import flask_csv as cv


app = Flask(__name__)
app.config['SECRET_KEY'] = 'frida'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://javi:javiersolis12@localhost:3306/Tuti'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class configuracion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.Integer)
    frec = db.Column(db.Integer)
    potmax = db.Column(db.Float())
    potmin = db.Column(db.Float())
    tempmax = db.Column(db.Integer)
    tempmin = db.Column(db.Integer)
    checkbox = db.Column(db.String(15))
    ip = db.Column(db.String(15))


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
    tempGabinete = db.Column(db.Float())
    hora = db.Column(db.Time())
    fecha = db.Column(db.Date())


class ahora(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    temperatura = db.Column(db.Float())
    humedad = db.Column(db.Float())
    canal1 = db.Column(db.Float())
    canal2 = db.Column(db.Float())
    canal3 = db.Column(db.Float())
    canal4 = db.Column(db.Float())
    tempGabinete = db.Column(db.Float())
    hora = db.Column(db.Time())

class alarmas(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    codigo = db.Column(db.String(10))
    descripcion = db.Column(db.String(100))
    hora_inicial = db.Column(db.Time())
    fec_inicial = db.Column(db.Date())
    estado = db.Column(db.String(10))


def menorQue(num1, num2):
    if (num1 < num2):
        return num1
    if (num2 < num1):
        return num2
    if (num1 == num2):
        return num1


def mayorQue(num1, num2):
    if (num1 > num2):
        return num1
    if (num2 > num1):
        return num2
    if (num1 == num2):
        return num1


def temperaturaMayorMenor():
    Mayor = 0
    Menor = 1000
    temperaturas = todo.query.with_entities(todo.temperatura)
    for temperatura in temperaturas:
        aux = temperatura[0]
        Mayor = mayorQue(Mayor, aux)
        Menor = menorQue(Menor, aux)
    return Mayor, Menor


def ch1MayorMenor():
    Mayor = 0
    Menor = 1000
    voltajes = todo.query.with_entities(todo.canal1)
    for voltaje in voltajes:
        aux = voltaje[0]
        Mayor = mayorQue(Mayor, aux)
        Menor = menorQue(Menor, aux)
    return Mayor, Menor


def ch2MayorMenor():
    Mayor = 0
    Menor = 1000
    voltajes = todo.query.with_entities(todo.canal2)
    for voltaje in voltajes:
        aux = voltaje[0]
        Mayor = mayorQue(Mayor, aux)
        Menor = menorQue(Menor, aux)
    return Mayor, Menor


def HumedadMayorMenor():
    Mayor = 0
    Menor = 1000
    humedades = todo.query.with_entities(todo.humedad)
    for humedad in humedades:
        aux = humedad[0]
        Mayor = mayorQue(Mayor, aux)
        Menor = menorQue(Menor, aux)
    return Mayor, Menor


def PromedioTemperatura():
    suma = 0
    aux = 0
    temperaturas = todo.query.with_entities(todo.temperatura)
    for temperatura in temperaturas:
        suma = suma + temperatura[0]
        aux += 1
    promedio = suma/aux
    return round(promedio, 3)


def PromedioHumedad():
    suma = 0
    aux = 0
    humedades = todo.query.with_entities(todo.humedad)
    for humedad in humedades:
        suma = suma + humedad[0]
        aux += 1
    promedio = suma/aux
    return round(promedio, 3)


@app.route('/')
def home():
    sensores = ahora.query.filter_by(id=1).first()
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    return render_template('index.html', titulo='DASHBOARD TUTI', graph=sensores, notificaciones = len(Alarmas))


@app.route('/configuracion')
def Vista_config():
    ConfiGlobal = configuracion.query.filter_by(id=1).first()
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    return render_template('vconf.html', data=ConfiGlobal, titulo="Configuracion del Sistema", notificaciones = len(Alarmas))


@app.route('/ChangeConfig', methods=['POST'])
def Actualizar_Config():
    nuevaConfi = configuracion.query.filter_by(id=1).first()
    nuevaConfi.tipo = request.form["antena"]
    nuevaConfi.frec = request.form["frecuencia"]
    nuevaConfi.potmax = request.form["potmax"]
    nuevaConfi.potmin = request.form["potmin"]
    nuevaConfi.tempmax = request.form["tempmax"]
    nuevaConfi.tempmin = request.form["tempmin"]
    if request.form.get('check'):
        nuevaConfi.checkbox = "con CCM"
        nuevaConfi.ip = request.form['ip']
    else:
        nuevaConfi.checkbox = "sin CCM"
        nuevaConfi.ip = '0.0.0.0'
    db.session.commit()
    return redirect(url_for('Vista_config'))


@app.route('/datos', methods=["GET", "POST"])
def data1():
    tmayor, tmenor = temperaturaMayorMenor()
    ch1Mayor, ch1Menor = ch1MayorMenor()
    ch2Mayor, ch2Menor = ch2MayorMenor()
    humMayor, humMenor = HumedadMayorMenor()
    PromTemp = PromedioTemperatura()
    PromHum = PromedioHumedad()
    sensores = ahora.query.filter_by(id=1).first()
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    contador = 0
    for alarma in Alarmas:
        contador += 1

    data = [(time() - 14400) * 1000,
            sensores.temperatura,
            sensores.humedad,
            round(sensores.canal1, 4),
            round(sensores.canal2, 4),
            round(sensores.canal3, 4),
            round(sensores.canal4, 4),
            tmayor,
            tmenor,
            ch1Mayor,
            ch1Menor,
            ch2Mayor,
            ch2Menor,
            humMayor,
            humMenor,
            PromTemp,
            PromHum,
            sensores.tempGabinete,
            contador]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response


@app.route('/Vgraficos')
def Vista_graficos():
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    return render_template("vgraficos.html", titulo="Gráficos", notificaciones = len(Alarmas))

@app.errorhandler(404)
def not_found(e):
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    return render_template("404.html", titulo="Error 404", notificaciones = len(Alarmas))

@app.route('/datosJSON/<fec>/', methods=['GET', 'POST'])
def ValoresJson(fec):
    xData = []
    data0 = []
    data1 = []
    data2 = []
    SalidaDatos = {}
    Datos = todo.query.filter_by(fecha=fec).all()
    for dato in Datos:
        aux = dato.hora
        NumeroHoras = int(aux.hour) + (int(aux.minute) / 100)
        xData.append(NumeroHoras)
        data0.append(dato.canal1)
        data1.append(dato.temperatura)
        data2.append(dato.humedad)
    SalidaDatos = {
        "xData": xData,
        "datasets": [{
            "name": "Potencia Recepción",
            "data": data0,
            "unit": "[V]",
            "type": "line",
            "valueDecimals": 1
        }, {
            "name": "Temperatura",
            "data": data1,
            "unit": "°C",
            "type": "line",
            "valueDecimals": 0
        }, {
            "name": "Humedad",
            "data": data2,
            "unit": "%",
            "type": "line",
            "valueDecimals": 0
        }]
    }
    return jsonify(SalidaDatos)

@app.route('/alarmas')
def MostrarAlarmas():
    Alarmas = alarmas.query.filter_by(estado='activo').all()
    return render_template('VistaAlarmas.html', notificaciones = len(Alarmas), datos = Alarmas, titulo="Alarmas")

@app.route("/prueba")
def index():
    return cv.send_csv([{"id": 42, "foo": "bar"}, {"id": 91, "foo": "baz"}],
                    "test.csv", ["id", "foo"])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
