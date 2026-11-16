"""Inteligencia de negocio: predicción de agotamiento, reposición sugerida, vencimientos,
productos sin rotación, capital en inventario y comparativos del marcador.

Solo lee datos existentes (no crea tablas ni toca el esquema de la base).
"""
import math
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from purchases.models import Compras
from sales.models import Detalleventa, Pedidos, Productos, Ventas

DIAS_VENTANA = 30          # ventana para medir el ritmo de ventas
DIAS_COBERTURA = 30        # a cuántos días de venta se quiere cubrir al reponer
DIAS_VENCIMIENTO = 90      # avisar de productos que vencen dentro de este plazo
DIAS_SIN_ROTACION = 60     # sin ventas en este plazo = sin rotación
UMBRAL_CRITICO = 7
UMBRAL_ATENCION = 15


def _ritmo_de_ventas(dias=DIAS_VENTANA):
    """Unidades vendidas por día de cada producto en los últimos ``dias`` días."""
    desde = timezone.localdate() - timedelta(days=dias)
    filas = (Detalleventa.objects
             .filter(estado=1, id_venta__estado=1, id_venta__fechareg__gte=desde)
             .values('id_producto').annotate(unidades=Sum('cantidad')))
    return {f['id_producto']: (f['unidades'] or 0) / dias for f in filas}


def _productos_activos():
    return list(Productos.objects.filter(estado=1).values(
        'id_producto', 'nombre_producto', 'cantidad', 'precio', 'precio_pub', 'fechaven', 'presentacion'))


def reposicion(ritmo=None, productos=None):
    """Productos que se agotarán pronto, con cuánto comprar para cubrir DIAS_COBERTURA días."""
    ritmo = _ritmo_de_ventas() if ritmo is None else ritmo
    productos = _productos_activos() if productos is None else productos
    salida = []
    for p in productos:
        stock = max(p['cantidad'], 0)
        vel = ritmo.get(p['id_producto'], 0)
        dias = None if vel <= 0 else stock / vel
        if stock == 0:
            nivel = 'critico'
        elif dias is not None and dias <= UMBRAL_CRITICO:
            nivel = 'critico'
        elif dias is not None and dias <= UMBRAL_ATENCION:
            nivel = 'atencion'
        else:
            continue
        sugerido = max(0, math.ceil(vel * DIAS_COBERTURA - stock)) if vel > 0 else 0
        salida.append({
            'id_producto': p['id_producto'], 'producto': p['nombre_producto'], 'stock': stock,
            'ventas_por_dia': round(vel, 2), 'dias_restantes': None if dias is None else round(dias, 1),
            'nivel': nivel, 'sugerido': sugerido, 'costo_estimado': round(sugerido * p['precio']),
        })
    salida.sort(key=lambda x: (x['dias_restantes'] if x['dias_restantes'] is not None else -1, x['stock']))
    return salida


def por_vencer(productos=None):
    productos = _productos_activos() if productos is None else productos
    limite = timezone.now() + timedelta(days=DIAS_VENCIMIENTO)
    ahora = timezone.now()
    salida = []
    for p in productos:
        if p['cantidad'] <= 0 or p['fechaven'] is None or p['fechaven'] > limite:
            continue
        dias = (p['fechaven'] - ahora).days
        salida.append({
            'id_producto': p['id_producto'], 'producto': p['nombre_producto'], 'stock': p['cantidad'],
            'vence': p['fechaven'].strftime('%d/%m/%Y'), 'dias': dias,
            'nivel': 'vencido' if dias < 0 else 'critico' if dias <= 30 else 'atencion',
            'valor': round(p['cantidad'] * p['precio']),
        })
    salida.sort(key=lambda x: x['dias'])
    return salida


def sin_rotacion(productos=None):
    """Productos con stock que no se han vendido en DIAS_SIN_ROTACION días (capital parado)."""
    productos = _productos_activos() if productos is None else productos
    ritmo = _ritmo_de_ventas(DIAS_SIN_ROTACION)
    salida = [{
        'id_producto': p['id_producto'], 'producto': p['nombre_producto'], 'stock': p['cantidad'],
        'capital': round(p['cantidad'] * p['precio']),
    } for p in productos if p['cantidad'] > 0 and p['id_producto'] not in ritmo]
    salida.sort(key=lambda x: -x['capital'])
    return salida[:10]


def capital(productos=None):
    productos = _productos_activos() if productos is None else productos
    unidades = sum(max(p['cantidad'], 0) for p in productos)
    costo = sum(max(p['cantidad'], 0) * p['precio'] for p in productos)
    publico = sum(max(p['cantidad'], 0) * p['precio_pub'] for p in productos)
    return {'unidades': unidades, 'costo': round(costo), 'publico': round(publico),
            'margen_potencial': round(publico - costo),
            'margen_pct': round((publico - costo) / publico * 100, 1) if publico else 0}


def inventario_inteligente():
    productos = _productos_activos()
    ritmo = _ritmo_de_ventas()
    rep = reposicion(ritmo, productos)
    return {
        'reposicion': rep, 'por_vencer': por_vencer(productos), 'sin_rotacion': sin_rotacion(productos),
        'capital': capital(productos),
        'inversion_sugerida': sum(r['costo_estimado'] for r in rep),
        'parametros': {'dias_ventana': DIAS_VENTANA, 'dias_cobertura': DIAS_COBERTURA,
                       'dias_vencimiento': DIAS_VENCIMIENTO, 'dias_sin_rotacion': DIAS_SIN_ROTACION},
    }


# ---------------------------------------------------------------- marcador con comparativos
def _variacion(actual, previo):
    if not previo:
        return None
    return round((actual - previo) / abs(previo) * 100, 1)


def _suma(modelo, campo_fecha, campo_valor, inicio, fin, **filtros):
    return modelo.objects.filter(**{f'{campo_fecha}__range': (inicio, fin)}, **filtros).aggregate(t=Sum(campo_valor))['t'] or 0


def resumen_marcador(hoy=None):
    """Mes actual (hasta hoy) frente al mismo tramo del mes anterior, más la serie de los últimos 14 días."""
    hoy = hoy or timezone.localdate()
    inicio = hoy.replace(day=1)
    fin_prev = inicio - timedelta(days=1)
    inicio_prev = fin_prev.replace(day=1)
    fin_prev_tramo = min(inicio_prev + timedelta(days=hoy.day - 1), fin_prev)       # mismo nº de días

    ventas = _suma(Ventas, 'fechareg', 'totalVenta', inicio, hoy, estado=1)
    ventas_prev = _suma(Ventas, 'fechareg', 'totalVenta', inicio_prev, fin_prev_tramo, estado=1)
    margen = _suma(Ventas, 'fechareg', 'margenGanancia', inicio, hoy, estado=1)
    margen_prev = _suma(Ventas, 'fechareg', 'margenGanancia', inicio_prev, fin_prev_tramo, estado=1)
    compras = _suma(Compras, 'fechareg', 'totalCompra', inicio, hoy, estado=1)
    compras_prev = _suma(Compras, 'fechareg', 'totalCompra', inicio_prev, fin_prev_tramo, estado=1)

    desde = hoy - timedelta(days=13)
    por_dia = {f['fechareg']: f['t'] for f in Ventas.objects.filter(fechareg__range=(desde, hoy), estado=1)
               .values('fechareg').annotate(t=Sum('totalVenta'))}
    serie = [round(por_dia.get(desde + timedelta(days=i), 0)) for i in range(14)]

    return {
        'ventas': {'valor': round(ventas), 'previo': round(ventas_prev), 'variacion': _variacion(ventas, ventas_prev), 'serie': serie},
        'margen': {'valor': round(margen), 'previo': round(margen_prev), 'variacion': _variacion(margen, margen_prev)},
        'compras': {'valor': round(compras), 'previo': round(compras_prev), 'variacion': _variacion(compras, compras_prev)},
        'pedidos': {'valor': Pedidos.objects.filter(estado='en proceso').count()},
        'margen_pct': round(margen / ventas * 100, 1) if ventas else 0,
        'periodo': {'inicio': str(inicio), 'hoy': str(hoy), 'previo_inicio': str(inicio_prev), 'previo_fin': str(fin_prev_tramo)},
    }


# ---------------------------------------------------------------- meta mensual de ventas
MESES = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def progreso_meta(hoy=None):
    """Avance de la meta de ventas del mes: ritmo esperado, proyección y venta diaria necesaria."""
    import calendar
    from control.models import MetaVentas

    hoy = hoy or timezone.localdate()
    dias_mes = calendar.monthrange(hoy.year, hoy.month)[1]
    inicio = hoy.replace(day=1)
    ventas = _suma(Ventas, 'fechareg', 'totalVenta', inicio, hoy, estado=1)

    # Meta sugerida: promedio de los 3 meses anteriores + 10 %, redondeada a 10.000
    totales, ref = [], inicio
    for _ in range(3):
        fin = ref - timedelta(days=1)
        ini = fin.replace(day=1)
        totales.append(_suma(Ventas, 'fechareg', 'totalVenta', ini, fin, estado=1))
        ref = ini
    promedio = sum(totales) / 3
    sugerida = int(round(promedio * 1.10 / 10000) * 10000) if promedio > 0 else None

    registro = MetaVentas.objects.filter(anio=hoy.year, mes=hoy.month).first()
    meta = registro.valor if registro else None
    proyeccion = ventas / hoy.day * dias_mes
    datos = {
        'anio': hoy.year, 'mes': hoy.month, 'mes_nombre': MESES[hoy.month], 'dia': hoy.day, 'dias_mes': dias_mes,
        'meta': meta, 'definida_por': registro.definida_por if registro else '', 'sugerida': sugerida,
        'ventas': round(ventas), 'proyeccion': round(proyeccion), 'ritmo_diario': round(ventas / hoy.day),
        'estado': 'sin_meta', 'pct': 0, 'esperado': 0, 'esperado_pct': round(hoy.day / dias_mes * 100, 1),
        'faltante': 0, 'diario_necesario': 0,
    }
    if meta:
        esperado = meta * hoy.day / dias_mes
        faltante = max(meta - ventas, 0)
        dias_restantes = dias_mes - hoy.day + 1
        razon = ventas / esperado if esperado else 0
        datos.update({
            'pct': round(ventas / meta * 100, 1), 'esperado': round(esperado), 'faltante': round(faltante),
            'diario_necesario': round(faltante / dias_restantes) if dias_restantes else 0,
            'estado': 'cumplida' if ventas >= meta else 'adelantada' if razon >= 1.05 else 'al_ritmo' if razon >= 0.95 else 'atrasada',
        })
    return datos
