import random
from datetime import datetime, timezone
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from config.mongodb import mongo

calificar = Blueprint('calificar', __name__)


@calificar.route('/finale', methods=['GET'])
def finale():
    return redirect(url_for('usuario.resena'))


@calificar.route('/productos', methods=['GET'])
def get_productos():
    productos = list(mongo.db.productos.find({}, {'_id': 0}))
    return render_template('resena.html', rol=session.get('rol'), productos=productos)


@calificar.route('/producto', methods=['POST'])
def create_productos():
    if session.get('rol') != 'dueno':
        return jsonify({'error': 'Solo los dueños pueden crear productos'}), 403

    nombre = request.form.get('nombre', '').strip()
    categoria = request.form.get('categoria', '').strip()
    precio = request.form.get('precio', '').strip()
    tipo_animal = request.form.get('tipo_animal', '').strip()
    if not nombre:
        return jsonify({'error': 'El campo nombre es obligatorio'}), 400

    producto = {
        '_id': f'OBJ{random.randint(0, 999)}',
        'nombre': nombre,
        'categoria': categoria,
        'precio': precio,
        'tipo_animal': tipo_animal,
        'usuario_id': session.get('user_id'),
    }
    mongo.db.productos.insert_one(producto)
    return redirect(url_for('calificar.get_productos'))


@calificar.route('/resena', methods=['POST'])
def create_resena():
    if session.get('rol') != 'dueno':
        return jsonify({'error': 'Solo los dueños pueden crear reseñas'}), 403

    calificacion = request.form.get('calificacion', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    if not calificacion:
        return jsonify({'error': 'El campo calificación es obligatorio'}), 400

    calificacion_data = {
        '_id': f'CA{random.randint(0, 999)}',
        'usuario_id': session.get('user_id'),
        'fecha': datetime.now(timezone.utc),
        'calificacion': calificacion,
        'descripcion': descripcion,
    }
    mongo.db.calificaciones.insert_one(calificacion_data)
    return redirect(url_for('calificar.get_productos'))


if __name__ == '__main__':
    calificar.run(debug=True)