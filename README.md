# TuiranFit · ui-fit-go

Sistema de gestión (ventas, compras, inventario, clientes, proveedores, pedidos) y tienda pública
para una distribuidora de suplementos. Django 4.2 + MySQL.

## Puesta en marcha (desarrollo, sin MySQL)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
copy .env.example .env          # y deja DB_ENGINE=sqlite
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py create_dev_tables
.\.venv\Scripts\python.exe manage.py seed_dev_data
.\.venv\Scripts\python.exe manage.py runserver 8090
```

Abre <http://127.0.0.1:8090/> e ingresa con `admin@tuiranfit.test` / `admin123`.
La tienda pública está en `/Brutality/`. Si el puerto 8090 estuviera ocupado usa otro libre (`runserver 8100`).

`seed_dev_data` también genera fotos de producto de ejemplo en `media/` (no se sube a git).

> Los modelos son `managed = False`: el esquema real vive en la base MySQL `ranfit`.
> `create_dev_tables` solo crea esas tablas para desarrollo y pruebas. **No usar contra producción.**

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Usan SQLite en memoria (`tuiranfitgo/settings_test.py`) y no envían correos reales.

## Reglas de negocio que cubren las pruebas

- **Inventario:** nunca queda en negativo. Las ventas descuentan con una operación atómica y fallan
  si no hay stock; anular una venta devuelve el stock una sola vez y reactivarla vuelve a validarlo.
- **Compras:** cantidades válidas, todo o nada, y no se puede anular una compra si el stock quedaría negativo.
- **Pedidos de la tienda:** el precio sale de la base de datos (no del navegador), se valida el stock
  por producto y un cliente existente no se sobrescribe.
- **Seguridad:** contraseñas con bcrypt (las antiguas en texto plano se migran al iniciar sesión),
  recuperación de cuenta que exige verificar el código, endpoints protegidos por sesión y permiso de módulo.

## Estructura útil

| Ruta | Qué es |
|---|---|
| `tuiranfitgo/inventory.py` | Reglas de stock y validación compartidas |
| `authenticator/security.py` | Hash y verificación de contraseñas |
| `tuiranfitgo/static/css/tuiran-theme.css` | Identidad visual "Arena" del panel |
| `tuiranfitgo/static/js/tuiran-fx.js` | Paleta de comandos (Ctrl+K), foco de luz, progreso |
| `tuiranfitgo/static/js/colombia.js` + `static/data/colombia.json` | Departamentos y municipios (datos locales) con buscador |
| `page/static/css/arena-store.css` | Estilo de la tienda pública |

## Variables de entorno

Ver `.env.example`. Nunca subas `.env` a git.
