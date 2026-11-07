import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from catalogo.models import Vehiculo, VehiculoImagen

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class Command(BaseCommand):
    help = 'Puebla la base de datos con un vehículo de prueba (Chevrolet S10 2004) e imágenes placeholder'

    def crear_imagen_placeholder(self, texto, subtitulo, color_fondo=(30, 41, 59)):
        """
        Genera una imagen JPEG en memoria usando Pillow con una estética moderna.
        """
        width = 800
        height = 500
        image = Image.new('RGB', (width, height), color=color_fondo)
        draw = ImageDraw.Draw(image)

        # Dibujar una cuadrícula/marca sutil de diseño automotor
        for y in range(0, height, 40):
            draw.line([(0, y), (width, y)], fill=(color_fondo[0] + 15, color_fondo[1] + 15, color_fondo[2] + 15), width=1)
        for x in range(0, width, 40):
            draw.line([(x, 0), (x, height)], fill=(color_fondo[0] + 15, color_fondo[1] + 15, color_fondo[2] + 15), width=1)

        # Marco decorativo
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(100, 116, 139), width=3)

        # Dibujar textos
        draw.text((40, 180), "AUTOMÓVILES SANTILLÁN", fill=(203, 213, 225))
        draw.text((40, 220), texto, fill=(255, 255, 255))
        draw.text((40, 260), subtitulo, fill=(148, 163, 184))
        draw.text((40, 430), "Foto ilustrativa de muestra", fill=(100, 116, 139))

        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando creación de vehículo de prueba..."))

        # Crear o actualizar la Chevrolet S10 2004
        vehiculo, creado = Vehiculo.objects.get_or_create(
            marca='Chevrolet',
            modelo='S10',
            anio=2004,
            defaults={
                'motor': '2.8 MWM',
                'transmision': Vehiculo.Transmision.MANUAL,
                'traccion': Vehiculo.Traccion.TRACCION_4X2,
                'combustible': Vehiculo.Combustible.DIESEL,
                'categoria': Vehiculo.Categoria.PICK_UP,
                'precio': 12500000.00,
                'destacado': True,
                'disponible': True,
                'descripcion': (
                    "Impecable Chevrolet S10 año 2004 en excelente estado de conservación general.\n\n"
                    "Equipada con el legendario y robusto motor 2.8 MWM Turbo Diesel intercooler, "
                    "reconocido por su durabilidad inquebrantable, bajo consumo y gran potencia. "
                    "Cuenta con caja manual de 5 velocidades, tracción 4x2, dirección hidráulica, "
                    "aire acondicionado funcionando perfectamente, levanta cristales eléctricos y "
                    "tapizados originales muy cuidados.\n\n"
                    "Ideal tanto para jornadas de trabajo exigente como para viajes largos en ruta. "
                    "Mantenimiento preventivo al día, cubiertas en óptimas condiciones, VTV vigente y "
                    "toda la documentación lista para transferir de inmediato. Aceptamos permutas de menor valor."
                ),
            }
        )

        if creado:
            self.stdout.write(self.style.SUCCESS(f"Vehículo creado: {vehiculo}"))
        else:
            self.stdout.write(self.style.WARNING(f"El vehículo ya existía: {vehiculo}"))

        # Crear fotos si no tiene aún
        if vehiculo.imagenes.count() == 0:
            if not PIL_AVAILABLE:
                self.stdout.write(
                    self.style.WARNING("Pillow no está instalado en este entorno aún. Instala requirements.txt para generar las imágenes.")
                )
                return

            self.stdout.write("Generando 3 imágenes placeholder de alta resolución...")

            fotos_data = [
                {
                    "nombre": "s10_frente.jpg",
                    "titulo": "CHEVROLET S10 2004 - 2.8 MWM",
                    "subtitulo": "Vista Frontal y Tres Cuartos",
                    "color": (15, 23, 42),  # Azul oscuro
                },
                {
                    "nombre": "s10_lateral.jpg",
                    "titulo": "CHEVROLET S10 2004 - PICK UP",
                    "subtitulo": "Vista Lateral y Caja de Carga",
                    "color": (30, 41, 59),  # Gris pizarra
                },
                {
                    "nombre": "s10_interior.jpg",
                    "titulo": "CHEVROLET S10 2004 - INTERIOR",
                    "subtitulo": "Habitáculo, Butacas y Tablero",
                    "color": (24, 24, 27),  # Zinc oscuro
                },
            ]

            for i, data in enumerate(fotos_data, start=1):
                buffer = self.crear_imagen_placeholder(
                    texto=data["titulo"],
                    subtitulo=data["subtitulo"],
                    color_fondo=data["color"]
                )
                img_obj = VehiculoImagen(
                    vehiculo=vehiculo,
                    orden=i
                )
                img_obj.imagen.save(data["nombre"], ContentFile(buffer.getvalue()), save=True)
                self.stdout.write(self.style.SUCCESS(f"  + Foto {i} adjuntada: {data['nombre']}"))

        # Vehículos adicionales para cubrir todas las categorías del catálogo
        otros_vehiculos = [
            {
                'marca': 'Toyota',
                'modelo': 'Corolla SEG',
                'anio': 2021,
                'motor': '2.0 Dynamic Force 170cv',
                'transmision': Vehiculo.Transmision.AUTOMATICA,
                'traccion': Vehiculo.Traccion.TRACCION_4X2,
                'combustible': Vehiculo.Combustible.NAFTA,
                'categoria': Vehiculo.Categoria.SEDAN,
                'precio': 22800000.00,
                'destacado': True,
                'disponible': True,
                'descripcion': 'Impecable Toyota Corolla versión tope de gama SEG. Caja automática CVT con levas al volante, paquete de seguridad Toyota Safety Sense (frenado autónomo y control crucero adaptativo). Tapizados en cuero, techo corredizo y services oficiales al día.',
                'fotos': [
                    {'nombre': 'corolla_1.jpg', 'titulo': 'TOYOTA COROLLA 2021 SEG', 'subtitulo': 'Sedan Ejecutivo - 2.0 Dynamic Force', 'color': (15, 23, 42)},
                    {'nombre': 'corolla_2.jpg', 'titulo': 'TOYOTA COROLLA 2021', 'subtitulo': 'Interior Cuero y Tablero Digital', 'color': (30, 41, 59)},
                ]
            },
            {
                'marca': 'Volkswagen',
                'modelo': 'Gol Trend Comfortline',
                'anio': 2018,
                'motor': '1.6 MSI 101cv',
                'transmision': Vehiculo.Transmision.MANUAL,
                'traccion': Vehiculo.Traccion.TRACCION_4X2,
                'combustible': Vehiculo.Combustible.NAFTA,
                'categoria': Vehiculo.Categoria.HATCHBACK,
                'precio': 10500000.00,
                'destacado': False,
                'disponible': True,
                'descripcion': 'Volkswagen Gol Trend 5 puertas versión Comfortline. Motor 1.6 de bajo consumo y excelente rendimiento. Equipado con aire acondicionado, dirección asistida, doble airbag, frenos ABS y conectividad Bluetooth.',
                'fotos': [
                    {'nombre': 'gol_1.jpg', 'titulo': 'VW GOL TREND 2018', 'subtitulo': 'Hatchback Urbano 1.6 MSI', 'color': (51, 65, 85)},
                    {'nombre': 'gol_2.jpg', 'titulo': 'VW GOL TREND 2018', 'subtitulo': 'Vista Trasera y Baúl', 'color': (30, 41, 59)},
                ]
            },
            {
                'marca': 'Renault',
                'modelo': 'Kangoo II Express',
                'anio': 2020,
                'motor': '1.5 dCi Turbo Diesel',
                'transmision': Vehiculo.Transmision.MANUAL,
                'traccion': Vehiculo.Traccion.TRACCION_4X2,
                'combustible': Vehiculo.Combustible.DIESEL,
                'categoria': Vehiculo.Categoria.UTILITARIO,
                'precio': 14900000.00,
                'destacado': False,
                'disponible': True,
                'descripcion': 'Renault Kangoo furgón en excelente estado para logística o trabajo. Puerta lateral corrediza, doble portón trasero, ganchos de sujeción y revestimiento interior. Motor turbo diesel de bajísimo consumo y gran autonomía.',
                'fotos': [
                    {'nombre': 'kangoo_1.jpg', 'titulo': 'RENAULT KANGOO 2020', 'subtitulo': 'Utilitario de Carga 1.5 dCi', 'color': (39, 39, 42)},
                ]
            },
            {
                'marca': 'Chevrolet',
                'modelo': 'Spin LTZ (7 Asientos)',
                'anio': 2019,
                'motor': '1.8 8v',
                'transmision': Vehiculo.Transmision.AUTOMATICA,
                'traccion': Vehiculo.Traccion.TRACCION_4X2,
                'combustible': Vehiculo.Combustible.GNC,
                'categoria': Vehiculo.Categoria.SIETE_ASIENTOS,
                'precio': 15800000.00,
                'destacado': True,
                'disponible': True,
                'descripcion': 'Chevrolet Spin versión LTZ con 3 filas de asientos (capacidad real para 7 pasajeros). Cuenta con equipo de GNC de 5ta generación bajo chasis. Ideal para familias numerosas o traslados. Pantalla MyLink y cámara de retroceso.',
                'fotos': [
                    {'nombre': 'spin_1.jpg', 'titulo': 'CHEVROLET SPIN 2019', 'subtitulo': 'Monovolumen Familiar 7 Asientos', 'color': (24, 24, 27)},
                    {'nombre': 'spin_2.jpg', 'titulo': 'CHEVROLET SPIN 2019', 'subtitulo': 'Capacidad 7 Plazas y Espacio', 'color': (15, 23, 42)},
                ]
            },
        ]

        for auto_data in otros_vehiculos:
            fotos = auto_data.pop('fotos')
            auto_obj, auto_creado = Vehiculo.objects.get_or_create(
                marca=auto_data['marca'],
                modelo=auto_data['modelo'],
                anio=auto_data['anio'],
                defaults=auto_data
            )
            if auto_creado:
                self.stdout.write(self.style.SUCCESS(f"Vehículo creado: {auto_obj}"))
                if PIL_AVAILABLE:
                    for j, f in enumerate(fotos, start=1):
                        buff = self.crear_imagen_placeholder(f['titulo'], f['subtitulo'], f['color'])
                        img_item = VehiculoImagen(vehiculo=auto_obj, orden=j)
                        img_item.imagen.save(f['nombre'], ContentFile(buff.getvalue()), save=True)
                        self.stdout.write(f"  + Foto {j} adjuntada para {auto_obj.marca}")

        self.stdout.write(self.style.SUCCESS("¡Proceso finalizado con éxito!"))

