from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Vehiculo, VehiculoImagen


class PanelLoginForm(AuthenticationForm):
    """Formulario de login estilizado con Bootstrap 5 para el panel de administración."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Usuario administrador',
            'autocomplete': 'username',
            'autofocus': True,
        }),
        label="Usuario"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        }),
        label="Contraseña"
    )


class VehiculoForm(forms.ModelForm):
    """Formulario para la creación y edición de vehículos."""
    class Meta:
        model = Vehiculo
        fields = [
            'marca',
            'modelo',
            'anio',
            'categoria',
            'motor',
            'transmision',
            'traccion',
            'combustible',
            'precio',
            'disponible',
            'destacado',
            'descripcion',
        ]
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Chevrolet, Toyota, Ford'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: S10, Hilux, Ranger, Corolla'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2024'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'motor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2.8 MWM Turbo, 2.0 TDI'}),
            'transmision': forms.Select(attrs={'class': 'form-select'}),
            'traccion': forms.Select(attrs={'class': 'form-select'}),
            'combustible': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12500000.00 (Opcional)'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escriba una descripción detallada del estado del vehículo, equipamiento, mantenimiento y documentación.'
            }),
        }

