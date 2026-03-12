video https://youtu.be/BKVgPHCKsUE
# 🌿 AgroControl — Campos Fértiles S.A.

Sistema de gestión agrícola con interfaz gráfica en Python y base de datos MySQL.

---

## 📁 Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `tkinter.py` | Interfaz gráfica principal (Python + Tkinter) |
| `agrocontrol+sp.sql` | Procedimientos almacenados MySQL (ejecutar una sola vez) |

---

## ⚙️ Requisitos

- Python 3.8 o superior
- XAMPP con MySQL/MariaDB activo
- Base de datos `agrocontrol` creada previamente

### Librerías Python necesarias
```
pip install mysql-connector-python
```
Tkinter viene incluido con Python, no requiere instalación adicional.

---

## 🚀 Instalación y puesta en marcha

### Paso 1 — Configurar la base de datos
1. Abre XAMPP y activa el módulo **MySQL**
2. Abre **phpMyAdmin** → selecciona la base `agrocontrol`
3. Ve a la pestaña **SQL**
4. Pega todo el contenido de `procedimientos_agrocontrol.sql`
5. Clic en **Continuar**
6. Verifica que aparezcan 35 procedimientos en la sección **Procedimientos** de tu base de datos

### Paso 2 — Configurar la conexión en Python
Abre `agrocontrol_sp.py` y edita el bloque `DB_CONFIG` (líneas 9–15):
```python
DB_CONFIG = {
    "host":     "localhost",   # dirección del servidor
    "port":     3306,          # puerto MySQL (defecto XAMPP)
    "user":     "root",        # tu usuario
    "password": "",            # tu contraseña (vacío en XAMPP por defecto)
    "database": "agrocontrol"  # nombre de la base de datos
}
```

### Paso 3 — Ejecutar la aplicación
```bash
python agrocontrol_sp.py
```

---

## 🖥️ Estructura de la interfaz

La ventana principal tiene **7 pestañas**, cada una con:
- **Panel izquierdo** → formulario de ingreso/edición de datos
- **Panel derecho** → tabla con todos los registros de la BD
- **Barra inferior** → botones de acción

| Pestaña | Tabla BD | Color |
|---|---|---|
| Fincas | `Fincas` | Verde oscuro |
| Cultivos | `cultivos` | Verde oliva |
| Insumos | `inventario` | Café |
| Maquinaria | `maquinaria` | Azul gris |
| Empleados | `empleados` | Morado |
| Cosechas | `cosecha` | Verde agua |
| Clientes | `clientes` | Rojo tierra |

---

## 🔘 Botones y su función

| Botón | Función |
|---|---|
| 💾 **Guardar** | Inserta un nuevo registro (`sp_Insert...`) |
| ✏️ **Actualizar** | Modifica el registro seleccionado (`sp_Update...`) |
| 🗑️ **Eliminar** | Elimina el registro seleccionado (`sp_Delete...`) |
| 🧹 **Limpiar** | Vacía todos los campos del formulario |
| 🔄 **Actualizar lista** | Recarga la tabla desde la base de datos |

---



