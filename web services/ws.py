from flask import Flask, jsonify, request
from flask_cors import CORS
import pymssql

app = Flask(__name__)
CORS(app)

# ===============================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ===============================
def get_db_connection():
    return pymssql.connect(
        server='localhost',      # o el host de tu contenedor SQL
        user='sam',
        password='Noticia123',  # cámbialo según tu setup
        database='noticias_financieras'
    )


@app.route('/')
def home():
    return jsonify({"mensaje": "API de Noticias Financieras funcionando"}), 200


# ===============================
# CRUD: NOTICIAS
# ===============================
@app.route('/noticias', methods=['GET'])
def obtener_noticias():
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("SELECT * FROM noticias ORDER BY fecha_publicacion DESC")
    noticias = cursor.fetchall()
    conn.close()
    return jsonify(noticias)


@app.route('/noticias', methods=['POST'])
def crear_noticia():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO noticias (titulo, resumen, contenido, fecha_publicacion, fuente, empresa)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['titulo'],
        data['resumen'],
        data['contenido'],
        data['fecha_publicacion'],
        data['fuente'],
        data['empresa']
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Noticia creada exitosamente"}), 201


@app.route('/noticias/<int:id>', methods=['DELETE'])
def eliminar_noticia(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM noticias WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Noticia eliminada"}), 200


# ===============================
# MAIN
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
