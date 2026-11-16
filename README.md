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

## Tablas nuevas (auditoría y metas)

A diferencia del resto del proyecto, la app `control` sí tiene migraciones. En tu base MySQL ejecuta **una vez**:

```powershell
.\.venv\Scripts\python.exe manage.py migrate control
```

Solo crea `control_registroauditoria` y `control_metaventas`; no toca ninguna tabla existente.
Alternativa manual: `control/sql/control_mysql.sql`.

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

## Funciones destacadas

- **Inteligencia de inventario** (dashboard): predice en cuántos días se agota cada producto según el ritmo real de ventas,
  sugiere cuánto reponer, avisa de lo que vence pronto y de capital parado en productos sin rotación.
  Genera una **orden de compra sugerida** en PDF.
- **Marcador comparativo:** ventas, margen y compras del mes frente al mismo tramo del mes anterior, con mini gráfica.
- **Venta rápida (POS):** `Ventas > Venta rápida`. Catálogo táctil, carrito, cliente y cobro en segundos (`F2` buscar, `F9` cobrar).
  Usa las mismas validaciones de stock del servidor.
- **Paleta de comandos** (`Ctrl+K`): navega por módulos y busca productos, clientes, proveedores, ventas y pedidos.
- **Exportar a CSV** cualquier listado (respeta el filtro de búsqueda; abre bien en Excel).
- **Informes PDF** con la marca: informes por rango de fechas, comprobantes de venta y compra (con QR) y orden de compra.
- **Auditoría** (`Usuarios > Auditoría`): quién hizo qué y cuándo, con el antes y el después de cada cambio
  (productos, clientes, proveedores, usuarios, ventas, compras, pedidos, inicios de sesión, informes). Filtros y exportación a CSV.
  Nunca guarda contraseñas. Auditar no puede romper la operación principal.
- **Meta mensual de ventas** (dashboard): barra de progreso con el ritmo esperado de hoy, proyección a fin de mes y
  cuánto vender por día para llegar. Sugiere una meta según los últimos 3 meses.
- **Contactar por WhatsApp** desde cada pedido, con el mensaje ya redactado según su estado.
- **Tienda:** insignias reales de "Más vendido" y "Últimas unidades".

## Estructura útil

| Ruta | Qué es |
|---|---|
| `tuiranfitgo/inventory.py` | Reglas de stock y validación compartidas |
| `dashboard/insights.py` | Predicción de agotamiento, reposición, vencimientos y comparativos |
| `tuiranfitgo/reports.py` | Generador de PDF con la identidad de marca |
| `authenticator/security.py` | Hash y verificación de contraseñas |
| `tuiranfitgo/static/css/tuiran-theme.css` | Identidad visual "Arena" del panel |
| `tuiranfitgo/static/js/tuiran-fx.js` | Paleta de comandos (Ctrl+K), foco de luz, progreso |
| `tuiranfitgo/static/js/colombia.js` + `static/data/colombia.json` | Departamentos y municipios (datos locales) con buscador |
| `page/static/css/arena-store.css` | Estilo de la tienda pública |

## Variables de entorno

Ver `.env.example`. Nunca subas `.env` a git.
