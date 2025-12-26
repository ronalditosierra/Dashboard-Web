
[![Flask](https://img.shields.io/badge/Flask-3.0.0-blue?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-003B57?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deploy-black?style=flat-square&logo=vercel)](https://vercel.com/)

## 📌 Contexto del Proyecto: Problemática Real

En el sector logístico del Caribe colombiano (Sincelejo - Cartagena - Barranquilla), las empresas suelen enfrentar una **fragmentación de datos**. El control de quién conduce qué vehículo y cuánto peso se está transportando se lleva habitualmente en hojas de cálculo propensas a errores.

**LOGI-SINC** centraliza la operación. Permite a los gerentes visualizar la capacidad real de su flota y la distribución de su personal en tiempo real, transformando la administración de activos de un proceso reactivo a uno proactivo.

---

## 🚀 Características Principales

* **📊 Dashboard Dinámico:** Gráficos de dona y circulares que se actualizan automáticamente según los registros de la base de datos (Cargos de empleados y Marcas de vehículos).
* **🛠️ Gestión de Activos (CRUD):** Interfaz robusta para la eliminación segura de registros con modales de confirmación con efecto `glassmorphism`.
* **🔍 Búsqueda Inteligente:** Filtro en tiempo real para localizar empleados, placas de vehículos o IDs sin recargar la página.
* **🌓 Soporte Dark Mode:** Interfaz optimizada para reducir la fatiga visual en entornos operativos nocturnos.
* **📱 Responsive Design:** Totalmente funcional en tablets y dispositivos móviles para supervisores en campo.

---

## 🛠️ Instalación y Ejecución

Sigue estos pasos para poner en marcha el entorno local:

### 1. Clonar y Entrar al Proyecto
```bash
git clone [https://github.com/tu-usuario/logi-sinc.git](https://github.com/tu-usuario/logi-sinc.git)
cd logi-sinc
2. Configurar Entorno VirtualBash# Crear entorno
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac/Linux)
source venv/bin/activate
3. Instalar DependenciasBashpip install -r requirements.txt
4. Inicializar y Poblar Base de DatosEste paso creará el archivo logistica.db con 100 registros generados dinámicamente:Bashpython init_db.py
5. Lanzar ServidorBashpython app.py
Acceso: http://127.0.0.1:5000🔐 Credenciales de Acceso (Demo)Utilice estas credenciales para acceder al sistema administrativo:AtributoCredencialUsuario Administradoradmin@sincelejo.comContraseña12345📁 Estructura del SoftwarePlaintext├── static/              # CSS compilado, librerías JS y recursos visuales
├── templates/           # Vistas Jinja2
│   ├── components/      # Modales, Toasts y Navegación modular
│   ├── base.html        # Layout maestro (Head, Footer, Navbar)
│   └── activos.html     # Dashboard principal y tablas de datos
├── app.py               # Lógica de servidor y consultas SQL dinámicas
├── init_db.py           # Script de generación de datos masivos (Faker logic)
├── logistica.db         # Base de datos relacional (SQLite)



