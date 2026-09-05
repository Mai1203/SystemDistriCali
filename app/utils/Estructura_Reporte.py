# Importaciones de reportlab (únicas y ordenadas)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing

# Importaciones de PyQt6 (unificadas)
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt6.QtGui import QPixmap  # Si necesitas para logo

# Otras importaciones estándar
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import os
import tempfile


def generar_pdf_caja_ingresos(caja, ingresos, egresos=None):
    """Genera un PDF estilizado con la información de la caja, los ingresos y los egresos registrados."""
    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"Caja_Ingresos_{fecha_actual}.pdf"

        # Diálogo de guardado con PyQt6
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            None,
            "Guardar Reporte",
            nombre_archivo,
            "Archivos PDF (*.pdf)"
        )

        if not ruta_archivo:
            print("El usuario canceló la selección del archivo.")
            return

        if not ruta_archivo.endswith('.pdf'):
            ruta_archivo += '.pdf'

        doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
        elementos = []

        estilos = getSampleStyleSheet()
        estilo_titulo = estilos["Title"]
        estilo_negrita = ParagraphStyle(
            name="Bold",
            parent=estilos["Normal"],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=10
        )

        elementos.append(Paragraph("<b>📄 Reporte de Caja e Ingresos</b>", estilo_titulo))
        elementos.append(Spacer(1, 0.3 * inch))

        # Tabla de información de caja
        datos_caja = [
            ["Fecha Apertura:", caja.Fecha_Apertura],
            ["Fecha Cierre:", caja.Fecha_Cierre],
            ["Monto Inicial:", f"${caja.Monto_Base}"],
            ["Monto Final:", f"${caja.Monto_Final_calculado}"],
        ]
        tabla_caja = Table(datos_caja, colWidths=[150, 250])
        tabla_caja.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.red),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.whitesmoke),
            ("BACKGROUND", (1, 0), (1, -1), colors.beige),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elementos.append(tabla_caja)
        elementos.append(Spacer(1, 0.5 * inch))

        elementos.append(Paragraph("<b>📊 Ingresos Registrados:</b>", estilo_negrita))

        # Preparar datos de ingresos
        datos_ingresos = [["ID", "Tipo", "M.Efectivo", "M.Transferencia", "Total"]]
        for ingreso in ingresos:
            monto_efectivo = ingreso.monto_efectivo or 0
            monto_transaccion = ingreso.monto_transaccion or 0
            total = monto_efectivo + monto_transaccion
            datos_ingresos.append([
                ingreso.ID_Ingreso,
                ingreso.tipo_ingreso,
                f"${monto_efectivo:,.2f}",
                f"${monto_transaccion:,.2f}",
                f"${total:,.2f}"
            ])

        # Totales
        total_efectivo = sum(i.monto_efectivo or 0 for i in ingresos)
        total_transferencia = sum(i.monto_transaccion or 0 for i in ingresos)
        total_general = total_efectivo + total_transferencia
        datos_ingresos.append([
            "", "TOTAL",
            f"${total_efectivo:,.2f}",
            f"${total_transferencia:,.2f}",
            f"${total_general:,.2f}"
        ])

        tabla_ingresos = Table(datos_ingresos, colWidths=[50, 100, 100, 100, 100])
        tabla_ingresos.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.red),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
        ]))
        elementos.append(tabla_ingresos)
        elementos.append(Spacer(1, 0.5 * inch))

        if egresos:
            elementos.append(Paragraph("<b>📉 Egresos Registrados:</b>", estilo_negrita))

            datos_egresos = [["ID", "Tipo", "Monto"]]
            for eg in egresos:
                monto = eg.Monto_Egreso or 0
                datos_egresos.append([
                    str(getattr(eg, 'ID_Egreso', '')),
                    getattr(eg, 'Tipo_Egreso', 'Egreso'),
                    f"${monto:,.2f}"
                ])

            total_egresos = sum(eg.Monto_Egreso or 0 for eg in egresos)
            datos_egresos.append([
                "", "TOTAL", f"${total_egresos:,.2f}"
            ])

            tabla_egresos = Table(datos_egresos, colWidths=[100, 200, 150])
            tabla_egresos.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.black),
            ]))
            elementos.append(tabla_egresos)
            elementos.append(Spacer(1, 0.5 * inch))

        # Gráfico de pastel
        porcentaje_efectivo = (total_efectivo / total_general) * 100 if total_general > 0 else 0
        porcentaje_transferencia = (total_transferencia / total_general) * 100 if total_general > 0 else 0

        dibujo = Drawing(400, 200)
        grafico_pastel = Pie()
        grafico_pastel.x = 50
        grafico_pastel.y = 50
        grafico_pastel.width = 300
        grafico_pastel.height = 125
        grafico_pastel.data = [total_efectivo, total_transferencia]
        grafico_pastel.labels = [
            f'Efectivo: {porcentaje_efectivo:.2f}%',
            f'Transferencia: {porcentaje_transferencia:.2f}%'
        ]
        grafico_pastel.slices[0].fillColor = colors.beige
        grafico_pastel.slices[1].fillColor = colors.lightgrey
        dibujo.add(grafico_pastel)
        elementos.append(dibujo)
        elementos.append(Spacer(1, 0.5 * inch))

        pie_pagina = Paragraph(f"<i>🔹 Reporte generado el {fecha_actual}.</i>", estilos["Italic"])
        elementos.append(pie_pagina)

        doc.build(elementos)

        # Mensaje con PyQt6
        QMessageBox.information(None, "Reporte Generado", f"PDF generado con éxito: {ruta_archivo}")

    except Exception as e:
        print(f"Error al generar el PDF: {e}")
        QMessageBox.critical(None, "Error", f"Error al generar el PDF: {e}")


def crear_pdf(ruta_archivo, productos, tipo):
    """Genera PDF simple para listados de productos."""
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    if tipo == "Bajo Stock":
        titulo = Paragraph("📌 <b>Reporte de Productos con Bajo Stock</b>", estilos['Title'])
    elif tipo == "Inactivos":
        titulo = Paragraph("📌 <b>Reporte de Productos Inactivos y Activos</b>", estilos['Title'])
    else:
        titulo = Paragraph("📌 <b>Reporte de Productos</b>", estilos['Title'])

    elementos.append(titulo)
    elementos.append(Spacer(1, 0.3 * inch))

    if tipo == "Bajo Stock":
        data = [["ID", "Nombre", "Stock"]]
    elif tipo == "Inactivos":
        data = [["ID", "Nombre", "Estado"]]
    else:
        data = [["ID", "Nombre", "Información"]]

    for producto in productos:
        # Asumiendo que producto es una tupla/listas con tres elementos
        data.append([producto[0], producto[1], producto[2]])

    table = Table(data, colWidths=[1.7 * inch, 2.8 * inch, 1 * inch])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    elementos.append(table)
    doc.build(elementos)


def generar_pdf_productos_mas_vendidos(productos):
    """Genera PDF para productos más vendidos."""
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    default_filename = f"Productos_Mas_Vendido_{fecha_actual}.pdf"

    # Diálogo con PyQt6
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Guardar Reporte productos mas vendidos",
        default_filename,
        "PDF files (*.pdf)"
    )

    if not file_path:
        print("Operación cancelada.")
        return

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    titulo_style = styles["h1"]
    titulo_style.alignment = 1
    titulo_style.textColor = colors.black
    titulo_style.fontName = 'Helvetica-Bold'

    fecha_style = ParagraphStyle(
        'Fecha',
        parent=styles['Normal'],
        fontSize=10,
        alignment=2,
        textColor=colors.grey
    )

    tabla_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    story = []

    # Logo (opcional)
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=100, height=100))
            story.append(Spacer(1, 0.2 * inch))
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

    story.append(Paragraph("Reporte de Productos Más Vendidos", titulo_style))
    story.append(Spacer(1, 0.1 * inch))

    fecha = Paragraph(f"Fecha de Exportación: {fecha_actual}", fecha_style)
    story.append(fecha)
    story.append(Spacer(1, 0.2 * inch))

    data = [["ID", "Nombre", "Unidades Vendidas"]]
    for producto in productos:
        data.append([producto.ID_Producto, producto.Nombre, producto.Total_Unidades_Vendidas])

    table = Table(data)
    table.setStyle(tabla_style)
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Top 3
    if len(productos) >= 3:
        top_3 = productos[:3]
        top_3_data = [["Posición", "Nombre", "Unidades Vendidas"]]
        for i, producto in enumerate(top_3):
            top_3_data.append([i + 1, producto.Nombre, producto.Total_Unidades_Vendidas])

        top_3_table = Table(top_3_data)
        top_3_table.setStyle(tabla_style)
        story.append(Paragraph("Top 3 Productos Más Vendidos", styles['h2']))
        story.append(top_3_table)

    doc.build(story)
    QMessageBox.information(None, "Reporte generado", "Reporte de productos mas vendidos guardado correctamente")


def generar_analisis_financiero(analisis, ingresos, egresos_lista):
    """Genera PDF de análisis financiero con gráficos."""
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    default_filename = f"Analisis_financiero_{fecha_actual}.pdf"

    # Diálogo con PyQt6
    file_path, _ = QFileDialog.getSaveFileName(
        None,
        "Guardar Reporte de Análisis Financiero",
        default_filename,
        "PDF files (*.pdf)"
    )

    if not file_path:
        print("Operación cancelada.")
        return

    # Cálculos de totales
    total_ingresos_efectivo = 0.0
    total_ingresos_transferencia = 0.0
    datos_ingresos = []

    for ing in ingresos:
        tipo_str = str(getattr(ing, "tipo_ingreso", None) or (len(ing) > 2 and ing[2]) or "")
        
        m_efectivo = float(getattr(ing, "monto_efectivo", None) or (len(ing) > 3 and ing[3]) or 0.0)
        m_transaccion = float(getattr(ing, "monto_transaccion", None) or (len(ing) > 4 and ing[4]) or 0.0)
        m_abono = float(getattr(ing, "monto", None) or (len(ing) > 6 and ing[6]) or 0.0)
        metodo = str(getattr(ing, "metodo_pago", None) or (len(ing) > 8 and ing[8]) or "")

        if m_efectivo or m_transaccion:
            tot = m_efectivo + m_transaccion
            total_ingresos_efectivo += m_efectivo
            total_ingresos_transferencia += m_transaccion
        elif m_abono:
            tot = m_abono
            if metodo == "Efectivo":
                total_ingresos_efectivo += m_abono
            else:
                total_ingresos_transferencia += m_abono
        else:
            tot = 0.0

        id_str = str(getattr(ing, "ID_Ingreso", None) or ing[0] or "")
        datos_ingresos.append([id_str[:8], tipo_str[:18], f"${tot:,.0f}"])

    total_ingresos = total_ingresos_efectivo + total_ingresos_transferencia

    total_egresos = sum(
        float(getattr(eg, "Monto_Egreso", None) or (len(eg) > 3 and eg[3]) or (len(eg) > 2 and eg[2]) or 0.0)
        for eg in egresos_lista
    )
    total_ganancias = sum(float(getattr(dato, "ganancia_por_factura", None) or (len(dato) > 5 and dato[5]) or 0.0) for dato in analisis)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        fontSize=16,
        alignment=1,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    section_title_style = styles['Heading2']

    elements.append(Paragraph("Informe de Análisis Financiero", title_style))
    elements.append(Paragraph(f"Generado: {fecha_actual}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Configuración de tablas
    ancho_columna = (doc.width - 1 * inch) / 2

    def crear_tabla_compacta(datos, encabezados, columna_derecha_index):
        tabla = Table([encabezados] + datos, colWidths=[ancho_columna * 0.3, ancho_columna * 0.4, ancho_columna * 0.3])
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3d5c95')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('LEADING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f8f8')),
            ('ALIGN', (columna_derecha_index, 1), (columna_derecha_index, -1), 'RIGHT'),
            ('PADDING', (columna_derecha_index, 0), (columna_derecha_index, -1), (0, 0, 10, 0))
        ])
        tabla.setStyle(estilo)
        return tabla

    # Preparar datos
    datos_ganancias = [
        [str(getattr(dato, "ID_Factura", None) or dato[0])[:8], str(getattr(dato, "Tipo_Ingreso", None) or dato[1])[:15], f"${float(getattr(dato, 'ganancia_por_factura', None) or dato[5] or 0.0):,.0f}"]
        for dato in analisis
    ]

    def dividir_en_chunks(datos, max_filas):
        return [datos[i:i + max_filas] for i in range(0, len(datos), max_filas)]

    espacio_disponible = doc.height - 2 * inch
    max_filas_por_pagina = min(int(espacio_disponible / 12), 40)

    chunks_ingresos = dividir_en_chunks(datos_ingresos, max_filas_por_pagina)
    chunks_ganancias = dividir_en_chunks(datos_ganancias, max_filas_por_pagina)

    # Páginas con tablas lado a lado
    for i in range(max(len(chunks_ingresos), len(chunks_ganancias))):
        if i == 0:
            elements.append(Paragraph("Análisis Financiero Detallado", title_style))
            elements.append(Spacer(1, 12))

        chunk_ing = chunks_ingresos[i] if i < len(chunks_ingresos) else []
        chunk_gan = chunks_ganancias[i] if i < len(chunks_ganancias) else []

        tabla_ing = crear_tabla_compacta(chunk_ing, ["ID", "INGRESOS", "MONTO"], 2)
        tabla_gan = crear_tabla_compacta(chunk_gan, ["ID", "GANANCIAS", "MONTO"], 2)

        container = Table(
            [
                [
                    Paragraph("INGRESOS" + (" (cont.)" if i > 0 else ""), section_title_style),
                    Paragraph("GANANCIAS" + (" (cont.)" if i > 0 else ""), section_title_style)
                ],
                [tabla_ing, tabla_gan]
            ],
            colWidths=[ancho_columna] * 2
        )
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        elements.append(container)

        if i < max(len(chunks_ingresos), len(chunks_ganancias)) - 1:
            elements.append(PageBreak())

    # Totales
    elements.append(Paragraph("Ingresos", section_title_style))
    elements.append(Paragraph(f"• Total de Ingresos: ${total_ingresos:,.2f}", styles['Normal']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Egresos", section_title_style))
    elements.append(Paragraph(f"• Total de Egresos: ${total_egresos:,.2f}", styles['Normal']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Ganancias", section_title_style))
    elements.append(Paragraph(f"• Total de Ganancias: ${total_ganancias:,.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Gráficos
    save_dir = tempfile.gettempdir()

    # Gráfico 1: Ingresos vs Egresos
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    labels = ['Ingresos', 'Egresos']
    sizes = [total_ingresos, total_egresos]
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#ff6666'])
    ax1.set_title('Distribución Ingresos/Egresos')
    ax1.axis('equal')
    chart1_filename = os.path.join(save_dir, "grafico_ingresos_egresos.png")
    plt.savefig(chart1_filename, format='png', bbox_inches='tight')
    plt.close(fig1)

    # Gráfico 2: Evolución de ganancias
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ganancias_por_dia = defaultdict(float)
    for dato in analisis:
        fecha = dato[4].date()  # Asumiendo dato[4] es datetime
        ganancias_por_dia[fecha] += dato[5]

    fechas = sorted(ganancias_por_dia.keys())
    ganancias = [ganancias_por_dia[f] for f in fechas]
    fechas_str = [f.strftime('%d/%m') for f in fechas]
    num_dias = len(ganancias)

    if num_dias == 1:
        fig2, (ax2, ax3) = plt.subplots(1, 2, figsize=(12, 4))
        ax2.bar(fechas_str, ganancias, color='#2ecc71', width=0.6)
        ax2.set_title(f'Ganancias Totales del {fechas_str[0]}')
        ax2.set_ylabel('Monto ($)')
        ax2.text(0, ganancias[0], f'${ganancias[0]:,.2f}', ha='center', va='bottom', fontweight='bold')

        ventas_del_dia = [(dato[4].strftime('%H:%M'), dato[5]) for dato in analisis]
        horas = [v[0] for v in ventas_del_dia]
        montos = [v[1] for v in ventas_del_dia]
        ax3.bar(horas, montos, color='#3498db')
        ax3.set_title('Desglose por ventas')
        ax3.set_ylabel('Monto ($)')
        plt.sca(ax3)
        plt.xticks(rotation=45, ha='right')
        for i, val in enumerate(montos):
            ax3.text(i, val, f'${val:,.2f}', ha='center', va='bottom', fontsize=8)
        plt.tight_layout()
    elif num_dias <= 15:
        bars = ax2.bar(fechas_str, ganancias, color='#2ecc71')
        ax2.set_title('Ganancias Diarias (Totales)')
        ax2.set_ylabel('Monto ($)')
        plt.xticks(rotation=45, ha='right')
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height, f'${height:,.2f}', ha='center', va='bottom', fontsize=8)
    else:
        ax2.plot(fechas_str, ganancias, marker='o', color='#2ecc71', linestyle='-', linewidth=2)
        ax2.set_title('Evolución de Ganancias Diarias')
        ax2.set_ylabel('Monto ($)')
        plt.xticks(rotation=45, ha='right')
        max_idx = np.argmax(ganancias)
        ax2.plot(fechas_str[max_idx], ganancias[max_idx], 'ro')
        ax2.annotate(f'Máximo: ${ganancias[max_idx]:,.2f}',
                     xy=(fechas_str[max_idx], ganancias[max_idx]),
                     xytext=(10, 10), textcoords='offset points',
                     bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                     arrowprops=dict(arrowstyle='->'))

    plt.tight_layout()
    chart2_filename = os.path.join(save_dir, "grafico_ganancias.png")
    plt.savefig(chart2_filename, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig2)

    elements.append(Paragraph("Análisis Gráfico", section_title_style))
    elements.append(Image(chart1_filename, width=280, height=200))
    elements.append(Image(chart2_filename, width=400, height=250))
    elements.append(Spacer(1, 12))

    # Conclusión
    elements.append(Paragraph("Conclusión", section_title_style))
    if total_ganancias > total_egresos:
        conclusion_text = "El análisis muestra que las ganancias fueron óptimas, indicando una buena salud financiera."
    else:
        conclusion_text = "El análisis indica que las ganancias no fueron óptimas, lo que podría requerir ajustes financieros."
    elements.append(Paragraph(conclusion_text, styles['Normal']))

    doc.build(elements)

    # Limpiar temporales
    try:
        os.remove(chart1_filename)
        os.remove(chart2_filename)
    except:
        pass

    QMessageBox.information(None, "Éxito", f"PDF generado exitosamente: {file_path}")