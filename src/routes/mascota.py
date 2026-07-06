import random
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from config.mongodb import mongo

mascota = Blueprint('mascota', __name__)


def _get_payload():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


@mascota.route('/formulario', methods=['GET'])
def formulario():
    if not session.get('user_id'):
        return redirect(url_for('hello'))
    return render_template('completarD.html')


@mascota.route('/registro', methods=['POST'])
def create_mascota():
    if not session.get('user_id'):
        return jsonify({'error': 'Debe iniciar sesión'}), 401

    payload = _get_payload()
    nombre = str(payload.get('nombre', '') or '').strip()
    tipoa = str(payload.get('tipoa', '') or '').strip()
    raza = str(payload.get('raza', '') or '').strip()
    edad = str(payload.get('edad', '') or '').strip()
    condicion = str(payload.get('condicion', '') or '').strip()
    tipop = str(payload.get('tipop', '') or '').strip()
    descripcion = str(payload.get('descripcion', '') or '').strip()
    fecha = str(payload.get('fecha', '') or '').strip()

    if not nombre:
        return jsonify({'error': 'El campo nombre es obligatorio'}), 400

    contador = mongo.db.mascotas.count_documents({'usuario_id': session['user_id']})
    if contador >= 10:
        return jsonify({'error': 'Solo puedes registrar hasta 10 mascotas'}), 400

    mascota_data = {
        '_id': f'MAS{session["user_id"]}{random.randint(0, 99)}',
        'usuario_id': session['user_id'],
        'nombre': nombre,
        'tipoanimal': tipoa,
        'raza': raza,
        'edad': edad,
        'condicion': condicion,
        'procedimientoMedico': {
            'tipoProcedimiento': tipop,
            'descripcion': descripcion,
            'fecha': fecha,
        },
    }
    mongo.db.mascotas.insert_one(mascota_data)
    return ({'message': 'Mascota registrada correctamente!'})


if __name__ == '__main__':
    mascota.run(debug=True)