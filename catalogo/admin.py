from django.contrib import admin
from django.utils.html import format_html
from .models import Vehiculo, VehiculoImagen


class VehiculoImagenInline(admin.TabularInline):
    """
    Permite subir hasta 20 imágenes directamente desde la misma pantalla
    de carga y edición del vehículo.
    """
    model = VehiculoImagen
    extra = 3            # Muestra 3 campos vacíos listos para subir fotos
    max_num = 20         # Límite máximo de 20 fotos por vehículo
    fields = ('imagen', 'orden', 'vista_previa')
    readonly_fields = ('vista_previa',)

    def vista_previa(self, obj):
        if obj.pk and obj.imagen:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="width: 90px; height: 60px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;" />'
                '</a>',
                obj.imagen.url
            )
        return "Sin vista previa"

    vista_previa.short_description = "Vista Previa"


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    inlines = [VehiculoImagenInline]

    list_display = (
        'foto_miniatura',
        'marca',
        'modelo',
        'anio',
        'categoria',
        'combustible',
        'transmision',
        'traccion',
        'disponible',
        'total_fotos',
    )
    list_filter = (
        'categoria',
        'combustible',
        'transmision',
        'traccion',
        'anio',
        'disponible',
    )
    search_fields = (
        'marca',
        'modelo',
        'motor',
        'descripcion',
    )
    list_editable = ('disponible',)
    ordering = ('-creado_el',)
    readonly_fields = ('creado_el', 'actualizado_el')

    fieldsets = (
        ('Identificación del Vehículo', {
            'fields': (('marca', 'modelo'), ('anio', 'categoria'))
        }),
        ('Mecánica y Transmisión', {
            'fields': (('motor', 'combustible'), ('transmision', 'traccion'))
        }),
        ('Detalles y Descripción', {
            'fields': ('descripcion', ('precio', 'disponible', 'destacado'))
        }),
        ('Auditoría', {
            'classes': ('collapse',),
            'fields': ('creado_el', 'actualizado_el'),
        }),
    )

    def foto_miniatura(self, obj):
        primera = obj.primera_imagen
        if primera and primera.imagen:
            return format_html(
                '<img src="{0}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 3px;" />',
                primera.imagen.url
            )
        return "—"

    foto_miniatura.short_description = "Foto"

    def total_fotos(self, obj):
        return obj.imagenes.count()

    total_fotos.short_description = "Fotos cargadas"

