import io
import os
from PIL import Image, ImageOps
from django.core.files.base import ContentFile


def convertir_imagen_a_webp(imagen_file, target_w=1280, target_h=800, quality=84):
    """
    Convierte cualquier archivo de imagen (JPG, PNG, HEIC, TIFF, etc.) al formato WebP optimizado,
    redimensionándolo y ajustándolo perfectamente al contenedor estándar del catálogo (1280x800 px).
    
    Características:
    - Corrige automáticamente la rotación según los metadatos EXIF (fotos de celulares verticales/horizontales).
    - Ajusta y centra la imagen al contenedor uniforme de 1280x800 px para evitar saltos o deformaciones.
    - Para fotos horizontales: utiliza encuadre inteligente centrado (ImageOps.fit).
    - Para fotos verticales: las centra en un lienzo de 1280x800 con fondo institucional (#01072c) sin recortar el vehículo.
    - Comprime eficientemente en WebP con calidad 84%, reduciendo el peso a ~100-180 KB.
    - Devuelve un ContentFile con extensión .webp listo para ser guardado por Django.
    """
    if not imagen_file:
        return imagen_file

    try:
        # Abrir imagen con Pillow
        img = Image.open(imagen_file)

        # Corregir orientación según metadatos EXIF del teléfono / cámara
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Manejo de modos de color
        es_transparente = img.mode in ('RGBA', 'LA')
        if not es_transparente and img.mode != 'RGB':
            img = img.convert('RGB')

        # Redimensionar y ajustar al contenedor estándar (1280x800)
        if img.width >= img.height:
            # Foto horizontal: ajustar y encuadrar al contenedor estándar sin deformar
            img_ajustada = ImageOps.fit(
                img,
                (target_w, target_h),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5)
            )
        else:
            # Foto vertical: centrar dentro del lienzo 1280x800 sin cortar el vehículo
            color_fondo = (0, 0, 0, 0) if es_transparente else (1, 7, 44)  # #01072c
            modo_lienzo = 'RGBA' if es_transparente else 'RGB'
            canvas = Image.new(modo_lienzo, (target_w, target_h), color=color_fondo)

            ratio = target_h / img.height
            nuevo_ancho = max(1, int(img.width * ratio))
            img_escalada = img.resize((nuevo_ancho, target_h), Image.Resampling.LANCZOS)
            offset_x = (target_w - nuevo_ancho) // 2

            if es_transparente:
                canvas.paste(img_escalada, (offset_x, 0), img_escalada)
            else:
                canvas.paste(img_escalada, (offset_x, 0))

            img_ajustada = canvas

        # Guardar en buffer WebP
        buffer = io.BytesIO()
        img_ajustada.save(buffer, format='WEBP', quality=quality, optimize=True)
        buffer.seek(0)

        # Generar nuevo nombre con extensión .webp
        nombre_original = getattr(imagen_file, 'name', 'imagen')
        nombre_base = os.path.splitext(os.path.basename(nombre_original))[0]
        nuevo_nombre = f"{nombre_base}.webp"

        nuevo_archivo = ContentFile(buffer.read(), name=nuevo_nombre)
        nuevo_archivo._ya_convertido_webp = True
        return nuevo_archivo

    except Exception:
        # Si ocurre algún error en la decodificación, retornar el archivo original
        return imagen_file

