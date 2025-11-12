# Servicios Web para login usando MSSQLServer como base de datos, además se adiciona una tabla 'personajes' que también usaremos como ejemplo

Este repositorio contiene un ejercicio de conexión a una instancia de **SQL Server** que corre dentro de un contenedor Docker en **GitHub Codespaces** utilizando el paquete **pymssql** para Python.

## Tecnologías utilizadas

* SQL Server: Motor de base de datos relacional, ejecutándose en Docker para facilitar su despliegue.
* Python 3: Lenguaje de programación para backend y servicios web.
* Flask: Framework para crear servicios web RESTful.
*pymssql: Librería para conectar Python con SQL Server.
*Flask-CORS: Para permitir llamadas HTTP desde un frontend o desde otras aplicaciones.
*Streamlit (opcional): Para crear un frontend simple que consuma los servicios web.
*Docker: Contenedor que ejecuta SQL Server de manera aislada.

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- **GitHub Codespaces** habilitado.
- **Docker** ejecutándose en tu Codespace.
- **Python 3** instalado.
- **pymssql** instalado en tu entorno Python.

### Iniciar la instancia de SQL Server en Docker

Para iniciar una instancia de **SQL Server** en un contenedor Docker, ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=Noticia123' \
   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
```

### Instalar sqlcmd
```sh
# Import Microsoft GPG key and repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Update and install
sudo apt update
sudo ACCEPT_EULA=Y apt install -y mssql-tools18 unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Usar sqlcmd para conectarse desde la terminal
```sh
sqlcmd -S localhost -U sa -P Noticia123 -C
```

### Crear la base de datos noticias_financieras
```sh
CREATE DATABASE noticias_financieras;
GO
```
### Usar la base de datos creada
```sh
USE noticias_financieras;
GO
```

### Crear la tabla noticias
```sh
CREATE TABLE noticias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(255) NOT NULL,
    contenido NVARCHAR(MAX) NOT NULL,
    fecha_publicacion DATETIME NOT NULL,
    fuente NVARCHAR(100),
    departamento NVARCHAR(100)
);
GO
```


###  Insertar una noticia de prueba
```sh
INSERT INTO noticias (titulo, contenido, fecha_publicacion, fuente, departamento)
VALUES ('Primera noticia', 'Contenido de la primera noticia', GETDATE(), 'Fuente XYZ', 'Finanzas');
GO
```

### Cerrar sqlcmd
```sh
EXIT
```

### Instalar librerías python
```sh
pip install pymssql flask flask-cors requests
```


# Probar servicios web

## Prerequisitos

- Se ejecutaron los comandos SQL previos


### Ejecución de servidor de servicios web

Ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:
Para el backend tenemos ws.py, que es el servicio web principal, desarrollado con Flask. Se encarga de exponer los endpoints RESTful que permiten interactuar con la base de datos. No tiene interfaz gráfica.

```sh
cd web\ services/
python ws.py

```
Para tener un frontend conectado al backend. Tenemos dos opciones. La primera es la interfaz de usuario, creada con Streamlit.
Se conecta al backend (ws.py) a través de las solicitudes HTTP para mostrar datos y permitir acciones.

```sh
cd web\ services/
streamlit run app.py

```
### Ejemplos para consumir servicios web desde la terminal

Abra **otra terminal**  (no cierre la terminal que está ejecutando el servidor), y ejecute el siguiente comando para probar el servicio web de autenticación:
```sh
curl http://127.0.0.1:8501/noticias
```

Obtener una noticia por ID:
```sh
curl http://127.0.0.1:8501/noticias/1
```

Crear una noticia:
```sh
curl -X POST http://127.0.0.1:8501/noticias \
-H "Content-Type: application/json" \
-d '{
  "titulo": "Nueva noticia",
  "contenido": "Contenido de ejemplo",
  "fecha_publicacion": "2025-11-09",
  "fuente": "El Financiero",
  "departamento": "Economía"
}'
```

Actualizar una noticia existente:
```sh
curl -X PUT http://127.0.0.1:8501/noticias/2 \
-H "Content-Type: application/json" \
-d '{
  "titulo": "Título actualizado",
  "contenido": "Contenido actualizado",
  "fecha_publicacion": "2025-11-09",
  "fuente": "El Financiero",
  "departamento": "Economía"
}'
```

Eliminar una noticia:
```sh
curl -X DELETE http://127.0.0.1:8501/noticias/2
```
