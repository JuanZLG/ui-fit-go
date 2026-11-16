"""Genera imágenes de ejemplo de producto con la identidad de la marca (solo desarrollo).

Dibuja con Pillow un envase negro con tajo rojo, el gorila y el nombre del producto,
más una tabla nutricional. Así la tienda y el panel se ven completos sin subir fotos.
"""
import math
import os
import textwrap

from django.conf import settings
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

RED = (229, 36, 43)
RED_BRIGHT = (255, 59, 48)
RED_DEEP = (155, 28, 34)
WHITE = (244, 244, 245)
BLACK = (8, 8, 9)


def _fuente(tamano, negrita=True):
    candidatos = (["impact.ttf", "Impact.ttf", "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"]
                  if negrita else ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"])
    for nombre in candidatos:
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    return ImageFont.load_default(size=tamano)


def _gorila():
    """El logo del gorila (blanco sobre negro) como imagen con transparencia."""
    ruta = os.path.join(settings.BASE_DIR, "tuiranfitgo", "static", "img", "gorille.png")
    try:
        base = Image.open(ruta).convert("L")
    except OSError:
        return None
    gorila = Image.new("RGBA", base.size, (255, 255, 255, 0))
    gorila.putalpha(base)
    return gorila


def _cilindro(ancho, alto, radio, acento):
    """Cuerpo cilíndrico con sombreado (oscuro en los bordes, brillo a la izquierda)."""
    cuerpo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(cuerpo)
    for x in range(ancho):
        t = x / (ancho - 1)
        luz = math.cos((t - 0.32) * math.pi * 1.05) ** 2         # brillo suave
        v = int(26 + 66 * luz)
        d.line([(x, 0), (x, alto)], fill=(v, v, v + 2, 255))
    # tajo diagonal de color
    tajo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    td = ImageDraw.Draw(tajo)
    td.polygon([(-40, alto * 0.60), (ancho + 40, alto * 0.30), (ancho + 40, alto * 0.50), (-40, alto * 0.80)], fill=acento + (255,))
    td.polygon([(-40, alto * 0.83), (ancho + 40, alto * 0.53), (ancho + 40, alto * 0.57), (-40, alto * 0.87)], fill=WHITE + (255,))
    cuerpo = Image.alpha_composite(cuerpo, tajo)
    # sombreado final encima del tajo para que siga el cilindro
    sombra = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sombra)
    for x in range(ancho):
        t = x / (ancho - 1)
        borde = abs(t - 0.45) * 2
        sd.line([(x, 0), (x, alto)], fill=(0, 0, 0, int(150 * borde ** 2.2)))
    cuerpo = Image.alpha_composite(cuerpo, sombra)
    mascara = Image.new("L", (ancho, alto), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, ancho - 1, alto - 1], radius=radio, fill=255)
    cuerpo.putalpha(ImageChops.multiply(cuerpo.getchannel("A"), mascara))
    return cuerpo


def _texto_centrado(draw, lienzo_ancho, y, texto, fuente, relleno, sombra=None):
    caja = draw.textbbox((0, 0), texto, font=fuente)
    x = (lienzo_ancho - (caja[2] - caja[0])) / 2 - caja[0]
    if sombra:
        draw.text((x + 3, y + 3), texto, font=fuente, fill=sombra)
    draw.text((x, y), texto, font=fuente, fill=relleno)
    return caja[3] - caja[1]


def _envase(nombre, marca, tamano, acento):
    W, H = 760, 860
    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # sombra de contacto
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([110, 770, 650, 835], fill=(0, 0, 0, 190))
    lienzo = Image.alpha_composite(lienzo, sombra.filter(ImageFilter.GaussianBlur(16)))

    # cuerpo + tapa
    cuerpo = _cilindro(520, 560, 46, acento)
    lienzo.alpha_composite(cuerpo, (120, 215))
    tapa = _cilindro(480, 170, 38, (30, 30, 32))
    lienzo.alpha_composite(tapa, (140, 80))
    d = ImageDraw.Draw(lienzo)
    d.rounded_rectangle([140, 196, 620, 222], radius=10, fill=acento)          # aro de color
    d.rounded_rectangle([160, 92, 600, 108], radius=8, fill=(255, 255, 255, 40))  # brillo de la tapa

    # gorila + marca
    gorila = _gorila()
    if gorila:
        g = gorila.resize((92, 94))
        lienzo.alpha_composite(g, (W // 2 - 46, 238))
    d = ImageDraw.Draw(lienzo)
    _texto_centrado(d, W, 345, "TUIRANFIT", _fuente(40), WHITE)

    # nombre del producto (hasta 3 líneas)
    lineas = textwrap.wrap(nombre.upper(), 16)[:3]
    y = 400
    for linea in lineas:
        alto = _texto_centrado(d, W, y, linea, _fuente(50), WHITE, sombra=(0, 0, 0, 200))
        y += alto + 12

    # subtítulo: marca y presentación sobre el tajo
    _texto_centrado(d, W, 668, f"{marca.upper()}  /  {tamano.upper()}", _fuente(22, negrita=False), WHITE)
    return lienzo


def _shaker(acento):
    W, H = 760, 860
    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([200, 780, 560, 835], fill=(0, 0, 0, 190))
    lienzo = Image.alpha_composite(lienzo, sombra.filter(ImageFilter.GaussianBlur(14)))
    cuerpo = _cilindro(330, 600, 40, acento)
    lienzo.alpha_composite(cuerpo, (215, 200))
    tapa = _cilindro(300, 120, 30, (28, 28, 30))
    lienzo.alpha_composite(tapa, (230, 110))
    d = ImageDraw.Draw(lienzo)
    d.rounded_rectangle([255, 68, 505, 120], radius=18, fill=(34, 34, 36))      # pico
    d.rounded_rectangle([230, 188, 530, 206], radius=8, fill=acento)
    gorila = _gorila()
    if gorila:
        lienzo.alpha_composite(gorila.resize((84, 86)), (W // 2 - 42, 300))
    d = ImageDraw.Draw(lienzo)
    _texto_centrado(d, W, 400, "SHAKER", _fuente(46), WHITE)
    _texto_centrado(d, W, 456, "PRO 700ML", _fuente(30), WHITE)
    return lienzo


def _cinturon(acento):
    W, H = 760, 860
    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse([70, 560, 690, 650], fill=(0, 0, 0, 170))
    lienzo = Image.alpha_composite(lienzo, sombra.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(lienzo)
    d.rounded_rectangle([60, 330, 700, 530], radius=40, fill=(22, 22, 24))
    d.rounded_rectangle([60, 330, 700, 372], radius=20, fill=(48, 48, 52))
    d.rectangle([60, 470, 700, 482], fill=acento)
    for x in range(100, 680, 36):
        d.line([(x, 345), (x - 18, 520)], fill=(255, 255, 255, 22), width=3)
    d.rounded_rectangle([318, 306, 448, 556], radius=20, outline=(205, 205, 210), width=14)   # hebilla
    d.rounded_rectangle([372, 418, 470, 436], radius=8, fill=(205, 205, 210))                 # lengüeta
    gorila = _gorila()
    if gorila:
        lienzo.alpha_composite(gorila.resize((74, 76)), (118, 380))
    d = ImageDraw.Draw(lienzo)
    d.text((540, 412), "TF", font=_fuente(54), fill=WHITE)
    return lienzo


def guardar_imagen_producto(slug, nombre, marca, tamano, forma="envase", acento=RED):
    """Crea la foto del producto y devuelve su ruta relativa a MEDIA_ROOT."""
    if forma == "shaker":
        img = _shaker(acento)
    elif forma == "cinturon":
        img = _cinturon(acento)
    else:
        img = _envase(nombre, marca, tamano, acento)
    img = img.crop(img.getbbox()) if img.getbbox() else img
    rel = f"landingproducts/products/{slug}.png"
    ruta = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    img.save(ruta, optimize=True)
    return rel


def guardar_tabla_nutricional(slug, nombre, porcion):
    """Tabla de información nutricional de ejemplo (fondo blanco, estilo etiqueta)."""
    W, H = 640, 820
    img = Image.new("RGB", (W, H), (250, 250, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([14, 14, W - 15, H - 15], outline=BLACK, width=6)
    d.text((40, 36), "INFORMACIÓN NUTRICIONAL", font=_fuente(40), fill=BLACK)
    d.text((40, 92), nombre.upper()[:34], font=_fuente(24, negrita=False), fill=(70, 70, 70))
    d.line([(40, 136), (W - 40, 136)], fill=BLACK, width=8)
    filas = [("Tamaño de porción", porcion), ("Porciones por envase", "30"), ("Calorías", "120 kcal"),
             ("Proteína", "24 g"), ("Carbohidratos", "3 g"), ("Azúcares", "1 g"), ("Grasa total", "1.5 g"),
             ("Sodio", "130 mg"), ("Calcio", "100 mg")]
    y = 156
    for izq, der in filas:
        d.text((40, y), izq, font=_fuente(28, negrita=False), fill=BLACK)
        caja = d.textbbox((0, 0), der, font=_fuente(28))
        d.text((W - 40 - (caja[2] - caja[0]), y), der, font=_fuente(28), fill=BLACK)
        d.line([(40, y + 46), (W - 40, y + 46)], fill=(190, 190, 190), width=2)
        y += 56
    d.rectangle([40, H - 120, W - 40, H - 54], fill=RED)
    d.text((58, H - 108), "FORJADO EN HIERRO", font=_fuente(38), fill=WHITE)
    rel = f"landingproducts/nutritiondex/{slug}.png"
    ruta = os.path.join(settings.MEDIA_ROOT, rel)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    img.save(ruta, optimize=True)
    return rel
