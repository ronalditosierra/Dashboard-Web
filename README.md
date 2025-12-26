# 🌀 LOGI-SINC: Sistema de Gestión Logística Inteligente

[![Flask](https://img.shields.io/badge/Flask-3.0.0-blue?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deploy-black?style=flat-square&logo=vercel)](https://vercel.com/)

---

## 📌 Contexto del Proyecto: Problemática Real
Este proyecto fue realizado en base a una problematica real que vive una empresa de logistica en la ciudad de Sincelejo - Sucre - Colombia, fue elaborado con fines educativos y para portafolio personal, todo lo que se encuentra es en base a mi analisis sobre la problematica y como abordarla de la mejor manera. Quiero recalcar el uso de la importacion de archivo excel ya que hoy en día se sigue utilizando excel como una base de datos, por lo que este sistema permite adaptarse a ese tipo de empresas.

Gracias por ver este proyecto! Aun soy un estudiante en proceso de aprendizaje!
---

## 🚀 Características Principales

- **📊 Dashboard Dinámico**  
  Gráficos de dona y circulares (Chart.js) alimentados por consultas SQL en tiempo real para visualizar:
  - Cargos de empleados  
  - Marcas de vehículos  

- **🛠️ Gestión de Activos**  
  Interfaz robusta para eliminar registros de forma segura, con:
  - Modales de confirmación personalizados  
  - Efectos visuales modernos  

- **🔍 Búsqueda Inteligente**  
  Filtro instantáneo en el cliente para localizar:
  - Empleados  
  - Placas de vehículos  
  - IDs  
  sin recargar la página.

- **🌓 Soporte Dark Mode**  
  Interfaz optimizada con Tailwind CSS para reducir la fatiga visual en operaciones 24/7.

- **📱 Responsive Design**  
  Totalmente funcional en dispositivos móviles, ideal para supervisores en patios, bodegas y rutas.

---

## 🛠️ Instalación y Ejecución Local

Sigue estos pasos para poner en marcha el entorno de desarrollo:

### 1 Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/logi-sinc.git
cd logi-sinc 
```
## 🔐 Credenciales de Acceso (Entorno de Pruebas)

Para acceder al panel administrativo y gestionar los activos logísticos, utilice las siguientes credenciales preconfiguradas en la base de datos:

> [!TIP]
> **Estado del Servidor:** Activo para pruebas de gestión de flota y personal.

| Atributo | Credencial de Acceso |
| :--- | :--- |
| 📧 **Correo Electrónico** | `admin@sincelejo.com` |
| 🔑 **Contraseña** | `12345` |
| 🛡️ **Rol asignado** | `Administrador` |

---
### 2. Configurar Entorno Virtual
# Crear entorno
```
python -m venv venv
```
# Activar (Windows)
```
venv\Scripts\activate
```
# Activar (Mac/Linux)
```
source venv/bin/activate
```
### 3. Inicializar y Poblar Base de Datos
Este script creará el archivo logistica.db
```
python database.py
```
### 4. Luego procedemos a ejecutar esto en la terminal lo que generará automáticamente 100 registros realistas para cada tabla:
```
python generador_excel.py
```
### 5. Luego dentro de la terminal ejecutamos el siguiente comando el cual nos ejecutara la aplicacion dandonos tambien la url donde tendremos que acceder de forma local.
http://localhost:5000/login
```
python app.py
```
###📁 Estructura del Software
```
├── static/              # CSS compilado, librerías JS y recursos visuales
├── templates/           # Vistas Jinja2
│   ├── components/      # Modales, Toasts y Navegación modular
│   ├── base.html        # Layout maestro (Head, Footer, Navbar)
│   └── activos.html     # Dashboard principal y tablas de datos
├── app.py               # Lógica de servidor y consultas SQL dinámicas
├── init_db.py           # Script de generación de datos masivos (100 registros)
├── logistica.db         # Base de datos relacional (SQLite)
├── requirements.txt     # Librerías necesarias para el despliegue
└── vercel.json          # Configuración para despliegue Cloud (Serverless)
```
---
## 👤 Autor
**Ronaldo Sierra Viloria** [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ronaldosierrav/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ronalditosierra)
