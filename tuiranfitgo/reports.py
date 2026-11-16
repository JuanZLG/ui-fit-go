"""Generador de PDF con la identidad de marca TuiranFit (informes y comprobantes).

Uso:
    informe = Informe('Informe de ventas', 'Del 15/10/2026 al 15/11/2026', 'Ventas')
    informe.tarjetas([('Total vendido', '$2.927.000'), ...])
    informe.seccion('Detalle de ventas')
    informe.tabla(['Fecha', 'Cliente', 'Total'], filas, [80, 300, 152], 'LLR', total=['', 'TOTAL', '$1'])
    pdf_bytes = informe.construir()
"""
import io
import os
from datetime import datetime
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

NEGRO = colors.HexColor('#000000')
ROJO = colors.HexColor('#E5242B')
ROJO_OSCURO = colors.HexColor('#9B1C22')
GRIS_FONDO = colors.HexColor('#F4F4F5')
GRIS_LINEA = colors.HexColor('#D4D4D8')
GRIS_TEXTO = colors.HexColor('#6C6C72')
TEXTO = colors.HexColor('#18181B')

ANCHO, ALTO = letter
MARGEN = 40
ALTO_CABECERA = 78
ANCHO_UTIL = ANCHO - 2 * MARGEN            # 532 pt

_IMG = os.path.join(settings.BASE_DIR, 'tuiranfitgo', 'static', 'img')


def cop(valor):
    """Pesos colombianos sin decimales: 1404000 -> $1.404.000"""
    try:
        return '$' + f'{round(float(valor)):,}'.replace(',', '.')
    except (TypeError, ValueError):
        return '$0'


def fecha(valor):
    return valor.strftime('%d/%m/%Y') if hasattr(valor, 'strftime') else str(valor or '')


def esc(valor):
    return escape(str(valor if valor is not None else ''))


def _estilo(nombre, **kw):
    base = dict(fontName='Helvetica', fontSize=9, leading=12, textColor=TEXTO)
    base.update(kw)
    return ParagraphStyle(nombre, **base)


E_CUERPO = _estilo('cuerpo')
E_PEQ = _estilo('pequeno', fontSize=7.5, leading=10, textColor=GRIS_TEXTO)
E_ETIQ = _estilo('etiqueta', fontName='Helvetica-Bold', fontSize=6.8, leading=9, textColor=GRIS_TEXTO)
E_VALOR = _estilo('valor', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=NEGRO)
E_SECCION = _estilo('seccion', fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=NEGRO)
E_CELDA = _estilo('celda', fontSize=8.3, leading=10.5)
E_CELDA_B = _estilo('celdab', fontName='Helvetica-Bold', fontSize=8.3, leading=10.5)
E_AVISO = _estilo('aviso', fontSize=9.5, leading=14, textColor=GRIS_TEXTO, alignment=TA_CENTER)


class _Canvas(canvas.Canvas):
    """Dibuja cabecera y pie en cada página (el pie necesita el total de páginas)."""

    def __init__(self, *args, informe=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._informe = informe
        self._paginas = []

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for estado in self._paginas:
            self.__dict__.update(estado)
            self._decorar(total)
            super().showPage()
        super().save()

    def _decorar(self, total):
        inf = self._informe
        self.saveState()
        # --- Cabecera negra ---
        self.setFillColor(NEGRO)
        self.rect(0, ALTO - ALTO_CABECERA, ANCHO, ALTO_CABECERA, stroke=0, fill=1)
        for archivo, x, y, w, h in (('gorille.png', MARGEN, ALTO - ALTO_CABECERA + 15, 47, 48),
                                    ('TextLogo.png', MARGEN + 60, ALTO - ALTO_CABECERA + 25, 86, 30.8)):
            ruta = os.path.join(_IMG, archivo)
            if os.path.exists(ruta):
                self.drawImage(ruta, x, y, w, h, mask=None)
        # tajo rojo inclinado y filo inferior
        self.setFillColor(ROJO)
        p = self.beginPath()
        base = ALTO - ALTO_CABECERA
        p.moveTo(ANCHO - 250, base); p.lineTo(ANCHO - 110, base); p.lineTo(ANCHO - 124, base + 7); p.lineTo(ANCHO - 264, base + 7); p.close()
        self.drawPath(p, stroke=0, fill=1)
        self.setFillColor(ROJO_OSCURO)
        self.rect(0, base - 2.5, ANCHO, 2.5, stroke=0, fill=1)
        # texto de la derecha
        self.setFillColor(colors.white)
        self.setFont('Helvetica-Bold', 15)
        self.drawRightString(ANCHO - MARGEN, ALTO - 34, inf.titulo.upper())
        self.setFillColor(colors.HexColor('#A1A1A6'))
        self.setFont('Helvetica', 8.5)
        self.drawRightString(ANCHO - MARGEN, ALTO - 50, inf.subtitulo or '')
        if inf.referencia:
            self.setFillColor(colors.HexColor('#FF5A52'))
            self.setFont('Helvetica-Bold', 7.5)
            self.drawRightString(ANCHO - MARGEN, ALTO - 63, inf.referencia.upper())
        # --- Pie ---
        self.setStrokeColor(GRIS_LINEA)
        self.setLineWidth(0.6)
        self.line(MARGEN, 38, ANCHO - MARGEN, 38)
        self.setFillColor(GRIS_TEXTO)
        self.setFont('Helvetica-Bold', 7)
        self.drawString(MARGEN, 26, 'TUIRANFIT  /  FORJADO EN HIERRO')
        self.setFont('Helvetica', 7)
        self.drawRightString(ANCHO - MARGEN, 26,
                             f'Generado el {datetime.now():%d/%m/%Y %H:%M}   ·   Página {self._pageNumber} de {total}')
        self.restoreState()


class Informe:
    def __init__(self, titulo, subtitulo='', referencia=''):
        self.titulo, self.subtitulo, self.referencia = titulo, subtitulo, referencia
        self.historia = []

    # ---------- bloques ----------
    def espacio(self, alto=10):
        self.historia.append(Spacer(1, alto))

    def parrafo(self, texto, estilo=E_CUERPO):
        self.historia.append(Paragraph(texto, estilo))

    def aviso(self, texto):
        self.espacio(24)
        t = Table([[Paragraph(esc(texto), E_AVISO)]], colWidths=[ANCHO_UTIL])
        t.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, GRIS_LINEA), ('BACKGROUND', (0, 0), (-1, -1), GRIS_FONDO),
                               ('TOPPADDING', (0, 0), (-1, -1), 26), ('BOTTOMPADDING', (0, 0), (-1, -1), 26),
                               ('LINEABOVE', (0, 0), (-1, 0), 2, ROJO)]))
        self.historia.append(t)

    def seccion(self, titulo):
        self.espacio(14)
        t = Table([['', Paragraph(esc(titulo).upper(), E_SECCION)]], colWidths=[5, ANCHO_UTIL - 5])
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, 0), ROJO), ('LEFTPADDING', (1, 0), (1, 0), 9),
                               ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        self.historia.extend([t, Spacer(1, 7)])

    def tarjetas(self, items):
        """Fila de indicadores: [(etiqueta, valor), ...] (hasta 4)."""
        n = len(items)
        hueco = 8
        ancho = (ANCHO_UTIL - hueco * (n - 1)) / n
        celdas, anchos, estilos = [], [], []
        for i, (etiqueta, valor) in enumerate(items):
            col = i * 2
            celdas.append([Paragraph(esc(etiqueta).upper(), E_ETIQ), Paragraph(esc(valor), E_VALOR)])
            anchos.append(ancho)
            estilos += [('BACKGROUND', (col, 0), (col, -1), GRIS_FONDO), ('LINEABOVE', (col, 0), (col, 0), 2.2, ROJO)]
            if i < n - 1:
                anchos.append(hueco)
        fila_a, fila_b = [], []
        for i, (cab, val) in enumerate(celdas):
            fila_a.append(cab); fila_b.append(val)
            if i < n - 1:
                fila_a.append(''); fila_b.append('')
        t = Table([fila_a, fila_b], colWidths=anchos)
        t.setStyle(TableStyle(estilos + [('LEFTPADDING', (0, 0), (-1, -1), 10), ('TOPPADDING', (0, 0), (-1, 0), 9),
                                         ('BOTTOMPADDING', (0, 0), (-1, 0), 0), ('TOPPADDING', (0, 1), (-1, 1), 1),
                                         ('BOTTOMPADDING', (0, 1), (-1, 1), 11)]))
        self.historia.append(t)

    def tabla(self, encabezados, filas, anchos, alineacion=None, total=None, zebra=True):
        """alineacion: cadena con L/C/R por columna, p. ej. 'LCRR'."""
        alineacion = alineacion or 'L' * len(encabezados)
        mapa = {'L': 'LEFT', 'C': 'CENTER', 'R': 'RIGHT'}
        cab_estilos = [ParagraphStyle(f'h{i}', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.white,
                                      alignment={'L': 0, 'C': 1, 'R': 2}[a]) for i, a in enumerate(alineacion)]
        cuerpo = [[Paragraph(esc(h).upper(), cab_estilos[i]) for i, h in enumerate(encabezados)]]
        cel_estilos = [ParagraphStyle(f'c{i}', parent=E_CELDA, alignment={'L': 0, 'C': 1, 'R': 2}[a]) for i, a in enumerate(alineacion)]
        for fila in filas:
            cuerpo.append([Paragraph(esc(v), cel_estilos[i]) for i, v in enumerate(fila)])
        estilos = [
            ('BACKGROUND', (0, 0), (-1, 0), NEGRO), ('LINEBELOW', (0, 0), (-1, 0), 2, ROJO),
            ('TOPPADDING', (0, 0), (-1, 0), 8), ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6), ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 1), (-1, -1), 0.4, GRIS_LINEA),
        ]
        if zebra:
            estilos.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_FONDO]))
        if total:
            bold = [ParagraphStyle(f't{i}', parent=E_CELDA_B, fontSize=9.5, alignment={'L': 0, 'C': 1, 'R': 2}[a]) for i, a in enumerate(alineacion)]
            cuerpo.append([Paragraph(esc(v), bold[i]) for i, v in enumerate(total)])
            estilos += [('LINEABOVE', (0, -1), (-1, -1), 1.6, ROJO), ('BACKGROUND', (0, -1), (-1, -1), GRIS_FONDO),
                        ('TOPPADDING', (0, -1), (-1, -1), 9), ('BOTTOMPADDING', (0, -1), (-1, -1), 9)]
        t = Table(cuerpo, colWidths=anchos, repeatRows=1)
        t.setStyle(TableStyle(estilos))
        self.historia.append(t)

    def ficha(self, pares, columnas=2):
        """Bloque de datos tipo 'Etiqueta / valor' en columnas."""
        filas, fila = [], []
        for etiqueta, valor in pares:
            fila.append([Paragraph(esc(etiqueta).upper(), E_ETIQ), Paragraph(esc(valor) or '—', E_CELDA_B)])
            if len(fila) == columnas:
                filas.append(fila); fila = []
        if fila:
            fila += [['', '']] * (columnas - len(fila)); filas.append(fila)
        ancho = ANCHO_UTIL / columnas
        data = [[Table([[c[0]], [c[1]]], colWidths=[ancho - 14]) for c in f] for f in filas]
        t = Table(data, colWidths=[ancho] * columnas)
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), GRIS_FONDO), ('LINEBEFORE', (0, 0), (0, -1), 2.2, ROJO),
                               ('LEFTPADDING', (0, 0), (-1, -1), 12), ('TOPPADDING', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                               ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        self.historia.append(t)

    def totales(self, lineas, total):
        """Caja de totales alineada a la derecha: lineas=[(etiqueta, valor)], total=(etiqueta, valor)."""
        filas = [[Paragraph(esc(a), E_PEQ), Paragraph(esc(b), ParagraphStyle('tv', parent=E_CELDA, alignment=TA_RIGHT))] for a, b in lineas]
        filas.append([Paragraph(f'<b>{esc(total[0]).upper()}</b>', ParagraphStyle('tt', parent=E_CELDA, textColor=colors.white, fontSize=9)),
                      Paragraph(f'<b>{esc(total[1])}</b>', ParagraphStyle('tt2', parent=E_CELDA, textColor=colors.white, fontSize=13, leading=16, alignment=TA_RIGHT))])
        caja = Table(filas, colWidths=[110, 120])
        caja.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 2, ROJO), ('BACKGROUND', (0, len(filas) - 1), (-1, -1), NEGRO),
                                  ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                                  ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                                  ('BACKGROUND', (0, 0), (-1, -2), GRIS_FONDO)]))
        envoltura = Table([['', caja]], colWidths=[ANCHO_UTIL - 230, 230])
        envoltura.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                                       ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
        self.historia.extend([Spacer(1, 12), KeepTogether(envoltura)])

    def adjuntar(self, flowable):
        self.historia.append(flowable)

    # ---------- salida ----------
    def construir(self):
        buffer = io.BytesIO()
        doc = BaseDocTemplate(buffer, pagesize=letter, leftMargin=MARGEN, rightMargin=MARGEN,
                              topMargin=ALTO_CABECERA + 24, bottomMargin=52,
                              title=f'{self.titulo} - TuiranFit', author='TuiranFit')
        marco = Frame(MARGEN, 52, ANCHO_UTIL, ALTO - ALTO_CABECERA - 24 - 52, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        doc.addPageTemplates([PageTemplate(id='base', frames=[marco])])
        doc.build(self.historia, canvasmaker=lambda *a, **k: _Canvas(*a, informe=self, **k))
        return buffer.getvalue()

    def respuesta(self, nombre_archivo):
        r = HttpResponse(self.construir(), content_type='application/pdf')
        r['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return r


def rango_de_fechas(post):
    """Lee fecha_inicio/fecha_fin (AAAA-MM-DD). Devuelve (inicio, fin) o lanza ValueError con un mensaje claro."""
    from datetime import date
    try:
        inicio = date.fromisoformat((post.get('fecha_inicio') or '').strip())
        fin = date.fromisoformat((post.get('fecha_fin') or '').strip())
    except ValueError:
        raise ValueError('Selecciona un rango de fechas válido (fecha de inicio y de fin).')
    if inicio > fin:
        raise ValueError('La fecha de inicio no puede ser posterior a la fecha de fin.')
    return inicio, fin
