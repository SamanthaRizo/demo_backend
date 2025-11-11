# Servicios Web para login usando MSSQLServer como base de datos, además se adiciona una tabla 'personajes' que también usaremos como ejemplo

Este repositorio contiene un ejercicio de conexión a una instancia de **SQL Server** que corre dentro de un contenedor Docker en **GitHub Codespaces** utilizando el paquete **pymssql** para Python.

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

### Crear la tabla de usuarios
```sh
CREATE TABLE usuarios (
   username VARCHAR(50) PRIMARY KEY,
   nombre_completo VARCHAR(255) NOT NULL,
   contrasena CHAR(40) NOT NULL
);
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
###  Agregar usuario ejemplo (Password123)
```sh
INSERT INTO usuarios VALUES 
('srizo', 'Samantha Rizo', 'cbfdac6008f9cab4083784cbd1874f76618d2a97');
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

```sh
cd web\ services/
python app.py

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
