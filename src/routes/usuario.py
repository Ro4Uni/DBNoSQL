from datetime import datetime, timezone
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from config.mongodb import mongo

usuario = Blueprint('usuario', __name__)


def _get_payload():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


@usuario.route('/registro', methods=['POST'])
def create_usuario():
    payload = _get_payload()
    rut = str(payload.get('rut', request.form.get('rut', '')) or '').strip()
    nombre = str(payload.get('nombre', request.form.get('nombre', '')) or '').strip()
    apellido = str(payload.get('apellido', request.form.get('apellido', '')) or '').strip()

    if not rut:
        return jsonify({'error': 'El campo rut es obligatorio'}), 400

    user_id = f'USU{rut}'
    usuario_data = {
        '_id': user_id,
        'rut': rut,
        'nombre': nombre,
        'apellido': apellido,
        'activo': True,
        'fecha_registro': datetime.now(timezone.utc),
    }
    mongo.db.usuarios.replace_one({'_id': user_id}, usuario_data, upsert=True)

    session['user_id'] = user_id
    session['user_rut'] = rut
    session['user_nombre'] = nombre
    session['user_apellido'] = apellido
    session['rol'] = None

    return redirect(url_for('usuario.eleccion'))


@usuario.route('/eleccion', methods=['GET'])
def eleccion():
    return render_template('eleccion.html')


@usuario.route('/seleccionar-rol', methods=['POST'])
def seleccionar_rol():
    rol = request.form.get('rol', '').strip().lower()
    if rol not in {'dueno', 'veterinaria', 'comercio'}:
        return jsonify({'error': 'Rol inválido'}), 400

    session['rol'] = rol
    return redirect(url_for('usuario.perfil', rol=rol))


@usuario.route('/resena', methods=['GET'])
def resena():
    rol = session.get('rol')
    return render_template('resena.html', rol=rol)


@usuario.route('/perfil/<rol>', methods=['GET', 'POST'])
def perfil(rol):
    if not session.get('user_id'):
        return redirect(url_for('hello'))

    if request.method == 'GET':
        if rol == 'dueno':
            return render_template('completarD.html')
        if rol == 'veterinaria':
            return render_template('completarV.html')
        if rol == 'comercio':
            return render_template('completarC.html')
        return jsonify({'error': 'Rol inválido'}), 400

    payload = _get_payload()
    if rol == 'dueno':
        correo = payload.get('correo')
        if not correo:
            return jsonify({'error': 'El campo correo es obligatorio'}), 400

        dueno = {
            '_id': f'DUE{session["user_id"]}',
            'usuario_id': session['user_id'],
            'correo': correo,
            'telefono': payload.get('telefono'),
            'fecha_nacimiento': payload.get('fecha_nacimiento'),
            'edad': payload.get('edad'),
            'direccion': {
                'calle': payload.get('calle'),
                'comuna': payload.get('comuna'),
                'region': payload.get('region'),
            },
            'activo': True,
            'fecha_registro': datetime.now(timezone.utc),
        }
        mongo.db.duenos.insert_one(dueno)
        return redirect(url_for('usuario.resena'))

    if rol == 'veterinaria':
        contacto = payload.get('correo') or payload.get('telefono')
        if not contacto:
            return jsonify({'error': 'El campo contacto es obligatorio'}), 400

        veterinaria = {
            '_id': f'VET{payload.get("rut_recinto", "")}',
            'rut_recinto': payload.get('rut_recinto'),
            'nombre_recinto': payload.get('nombre_recinto'),
            'especialidad': payload.get('especialidad'),
            'direccion': {
                'calle': payload.get('calle'),
                'comuna': payload.get('comuna'),
                'region': payload.get('region'),
            },
            'contacto': {
                'telefono': payload.get('telefono'),
                'correo': payload.get('correo'),
            },
            'usuarios': [session['user_id']],
            'activo': True,
            'tiempo_actividad': payload.get('tiempo_actividad'),
            'fecha_registro': datetime.now(timezone.utc),
        }
        mongo.db.veterinarias.insert_one(veterinaria)
        return redirect(url_for('usuario.resena'))

    if rol == 'comercio':
        contacto = payload.get('correo') or payload.get('telefono')
        if not contacto:
            return jsonify({'error': 'El campo contacto es obligatorio'}), 400

        comercio = {
            '_id': f'COM{payload.get("rut_recinto", "")}',
            'rut_recinto': payload.get('rut_recinto'),
            'nombre_recinto': payload.get('nombre_recinto'),
            'categoria': payload.get('categoria'),
            'direccion': {
                'calle': payload.get('calle'),
                'comuna': payload.get('comuna'),
                'region': payload.get('region'),
            },
            'contacto': {
                'telefono': payload.get('telefono'),
                'correo': payload.get('correo'),
            },
            'usuarios': [session['user_id']],
            'activo': True,
            'tiempo_actividad': payload.get('tiempo_actividad'),
            'fecha_registro': datetime.now(timezone.utc),
        }
        mongo.db.comercios.insert_one(comercio)
        return redirect(url_for('usuario.resena'))

    return jsonify({'error': 'Rol inválido'}), 400


if __name__ == '__main__':
    usuario.run(debug=True)