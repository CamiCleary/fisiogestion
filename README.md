# 💆‍♀️ FisioGestión

**FisioGestión** es un sistema integral desarrollado con **Python y Django** para la gestión eficiente de pacientes, tratamientos y pagos en un consultorio de fisioterapia.

Su objetivo es facilitar el trabajo administrativo y clínico, centralizando la información médica, financiera y operativa del consultorio en una sola plataforma intuitiva y personalizable.

---

## 🚀 Características principales

- 📋 Registro y gestión de pacientes.
- 🩺 Administración de tratamientos y evolución por sesión.
- 📅 Control de citas y disponibilidad.
- 📊 Generación de reportes mensuales con estadísticas de atención (cantidad de pacientes vistos, tratamientos aplicados, ingresos, etc.).
- 💬 Canal de comunicación con el paciente para seguimiento y consultas.
- 🧑‍💻 **Módulo de Telemedicina**:
  - Realización de consultas virtuales y sesiones de fisioterapia en línea.
  - Envío de ejercicios guiados y planes de tratamiento personalizados mediante videos.
- 💰 Módulo de gestión de pagos con soporte para:
  - Transferencias bancarias
  - Pago móvil
  - Billeteras digitales (Zinli, etc.)
  - Códigos QR
  - Pagos en efectivo y contra entrega
- 🔐 Sistema de roles y permisos.
- 💻 Interfaz responsiva creada desde cero (Figma → HTML + Bootstrap + Django). (podria ser tailwind)

---

## 🛠️ Tecnologías utilizadas

- Python 3
- Django
- HTML5 + CSS3
- Bootstrap 5
- MySQL
- WebRTC o servicios de terceros para videollamadas (en módulo de telemedicina) (en revisión)
- Herramientas multimedia para envío y reproducción de videos de ejercicios
- Figma (prototipo de interfaz)

---

## 📦 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/CamiCleary/fisiogestion.git
cd fisiogestion
