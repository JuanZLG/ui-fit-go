"""Enlaces de WhatsApp con el mensaje ya redactado para cada pedido."""
import re
from urllib.parse import quote

PREFIJO_COLOMBIA = '57'


def normalizar_celular(numero):
    """'300 123 4567' -> '573001234567'. Devuelve '' si no parece un celular válido."""
    digitos = re.sub(r'\D', '', str(numero or ''))
    if digitos.startswith('00'):
        digitos = digitos[2:]
    if len(digitos) == 10 and digitos.startswith('3'):
        return PREFIJO_COLOMBIA + digitos
    if len(digitos) == 12 and digitos.startswith(PREFIJO_COLOMBIA):
        return digitos
    return digitos if 11 <= len(digitos) <= 15 else ''


def _cop(valor):
    return '$' + f'{round(float(valor or 0)):,}'.replace(',', '.')


def mensaje_pedido(pedido, cliente, detalles):
    """Texto según el estado del pedido (en proceso, confirmado o cancelado)."""
    nombre = (getattr(cliente, 'nombres', '') or '').split(' ')[0] or 'cliente'
    total = _cop(pedido.total_pedido)
    productos = ', '.join(f'{d.cantidad}× {d.id_producto.nombre_producto}' for d in detalles) or 'tu pedido'
    if pedido.estado == 'confirmado':
        return (f'Hola {nombre}, tu pedido #{pedido.id_pedido} por {total} ya fue confirmado. '
                f'En breve te contactamos con los datos del despacho. ¡Gracias por tu compra en TuiranFit!')
    if pedido.estado == 'cancelado':
        return (f'Hola {nombre}, tu pedido #{pedido.id_pedido} fue cancelado. '
                f'Si quieres retomarlo o tienes dudas, escríbenos y te ayudamos. — TuiranFit')
    entrega = ', '.join(x for x in (getattr(cliente, 'direccion', ''), getattr(cliente, 'barrio', '')) if x)
    confirmar = f'¿Nos confirmas la dirección de entrega ({entrega})?' if entrega else '¿Nos confirmas tus datos de entrega?'
    return (f'Hola {nombre}, te escribimos de TuiranFit. Recibimos tu pedido #{pedido.id_pedido} ({productos}) '
            f'por un total de {total}. {confirmar} ¡Gracias!')


def url_whatsapp(celular, mensaje):
    numero = normalizar_celular(celular)
    return f'https://wa.me/{numero}?text={quote(mensaje)}' if numero else ''
