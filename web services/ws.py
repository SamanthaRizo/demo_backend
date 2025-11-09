# pip install pymssql flask flask-cors requests
import pymssql
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SERVER = 'localhost'
DATABASE = 'noticias_financieras'
USERNAME = 'sa'
PASSWORD = 'Noticia123'


def get_db_connection():
    try:
        conn = pymssql.connect(
            server=SERVER, port=1433, database=DATABASE, user=USERNAME, password=PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None


# --- Servicios CRUD para la tabla 'noticias' ---

# Obtener todas las noticias
@app.route('/noticias', methods=['GET'])
def get_noticias():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT id, titulo, contenido, fecha_publicacion, fuente, departamento FROM noticias ORDER BY fecha_publicacion DESC"
            )
            noticias = cursor.fetchall()
            return jsonify(noticias), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener noticias: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Obtener una noticia por ID
@app.route('/noticias/<int:id>', methods=['GET'])
def get_noticia(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute(
                "SELECT id, titulo, contenido, fecha_publicacion, fuente, departamento FROM noticias WHERE id = %d", (id,)
            )
            noticia = cursor.fetchone()
            if noticia:
                return jsonify(noticia), 200
            else:
                return jsonify({'mensaje': 'Noticia no encontrada'}), 404
        except Exception as e:
            return jsonify({'error': f'Error al obtener noticia: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Crear una nueva noticia
@app.route('/noticias', methods=['POST'])
def create_noticia():
    data = request.get_json()
    titulo = data.get('titulo')
    contenido = data.get('contenido')
    fecha_publicacion = data.get('fecha_publicacion')
    fuente = data.get('fuente')
    departamento = data.get('departamento')

    if not titulo or not contenido or not fecha_publicacion or not fuente or not departamento:
        return jsonify({'error': 'Se requieren todos los campos'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO noticias (titulo, contenido, fecha_publicacion, fuente, departamento) VALUES (%s, %s, %s, %s, %s)",
                (titulo, contenido, fecha_publicacion, fuente, departamento)
            )
            conn.commit()
            return jsonify({'mensaje': 'Noticia creada exitosamente'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al crear noticia: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Actualizar una noticia existente
@app.route('/noticias/<int:id>', methods=['PUT'])
def update_noticia(id):
    data = request.get_json()
    titulo = data.get('titulo')
    contenido = data.get('contenido')
    fecha_publicacion = data.get('fecha_publicacion')
    fuente = data.get('fuente')
    departamento = data.get('departamento')

    if not titulo or not contenido or not fecha_publicacion or not fuente or not departamento:
        return jsonify({'error': 'Se requieren todos los campos'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE noticias SET titulo = %s, contenido = %s, fecha_publicacion = %s, fuente = %s, departamento = %s WHERE id = %d",
                (titulo, contenido, fecha_publicacion, fuente, departamento, id)
            )
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({'mensaje': 'Noticia actualizada exitosamente'}), 200
            else:
                return jsonify({'mensaje': 'Noticia no encontrada'}), 404
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al actualizar noticia: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


# Eliminar una noticia por ID
@app.route('/noticias/<int:id>', methods=['DELETE'])
def delete_noticia(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM noticias WHERE id = %d", (id,))
            conn.commit()
            if cursor.rowcount > 0:
                return jsonify({'mensaje': 'Noticia eliminada exitosamente'}), 200
            else:
                return jsonify({'mensaje': 'Noticia no encontrada'}), 404
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al eliminar noticia: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000)
