from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import convertir_imagen_a_webp


class Vehiculo(models.Model):
    # Opciones de Transmisión
    class Transmision(models.TextChoices):
        MANUAL = 'Manual', 'Manual'
        AUTOMATICA = 'Automática', 'Automática'

    # Opciones de Tracción
    class Traccion(models.TextChoices):
        TRACCION_4X2 = '4x2', '4x2'
        TRACCION_4X4 = '4x4', '4x4'
        AWD = 'AWD', 'AWD'

    # Opciones de Combustible
    class Combustible(models.TextChoices):
        NAFTA = 'Nafta', 'Nafta'
        DIESEL = 'Diesel', 'Diesel'
        GNC = 'GNC', 'GNC'
        HIBRIDO = 'Híbrido', 'Híbrido'
        ELECTRICO = 'Eléctrico', 'Eléctrico'

    # Opciones de Categoría
    class Categoria(models.TextChoices):
        PICK_UP = 'Pick up', 'Pick up'
        HATCHBACK = 'Hatchback', 'Hatchback'
        SEDAN = 'Sedan', 'Sedan'
        UTILITARIO = 'Utilitario', 'Utilitario'
        SIETE_ASIENTOS = '7 asientos', '7 asientos'

    # Campos principales
    marca = models.CharField(max_length=60, verbose_name='Marca')
    modelo = models.CharField(max_length=60, verbose_name='Modelo')
    anio = models.PositiveIntegerField(
        verbose_name='Año',
        validators=[MinValueValidator(1950), MaxValueValidator(2035)]
    )
    motor = models.CharField(max_length=80, verbose_name='Motor', help_text='Ej: 2.8 MWM, 1.6 MSI, etc.')
    transmision = models.CharField(
        max_length=20,
        choices=Transmision.choices,
        default=Transmision.MANUAL,
        verbose_name='Transmisión'
    )
    traccion = models.CharField(
        max_length=10,
        choices=Traccion.choices,
        default=Traccion.TRACCION_4X2,
        verbose_name='Tracción'
    )
    combustible = models.CharField(
        max_length=20,
        choices=Combustible.choices,
        default=Combustible.NAFTA,
        verbose_name='Combustible'
    )
    categoria = models.CharField(
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.SEDAN,
        verbose_name='Categoría'
    )
    descripcion = models.TextField(verbose_name='Descripción detallada')

    # Campos complementarios
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio (ARS/USD)',
        help_text='Opcional. Dejar vacío para consultar precio.'
    )
    destacado = models.BooleanField(default=False, verbose_name='Vehículo Destacado')
    disponible = models.BooleanField(default=True, verbose_name='Disponible para venta')
    creado_el = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')
    actualizado_el = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        ordering = ['-creado_el']

    def __str__(self):
        return f"{self.marca} {self.modelo} {self.anio} ({self.categoria})"

    def get_absolute_url(self):
        return reverse('catalogo:detalle_vehiculo', kwargs={'pk': self.pk})

    @property
    def primera_imagen(self):
        """Devuelve la primera imagen asociada o None si no tiene."""
        return self.imagenes.first()


class VehiculoImagen(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='imagenes',
        verbose_name='Vehículo'
    )
    imagen = models.ImageField(
        upload_to='vehiculos/%Y/%m/',
        verbose_name='Fotografía'
    )
    orden = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Menor número se mostrará primero'
    )
    subido_el = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')

    class Meta:
        verbose_name = 'Foto del vehículo'
        verbose_name_plural = 'Fotos del vehículo'
        ordering = ['orden', 'id']

    def __str__(self):
        return f"Foto #{self.id} de {self.vehiculo.marca} {self.vehiculo.modelo}"

    def save(self, *args, **kwargs):
        # Convertir automáticamente a WebP si no ha sido convertida aún
        if self.imagen and not getattr(self.imagen, '_ya_convertido_webp', False):
            nombre = getattr(self.imagen, 'name', '')
            if not nombre.lower().endswith('.webp'):
                self.imagen = convertir_imagen_a_webp(self.imagen)
        super().save(*args, **kwargs)

