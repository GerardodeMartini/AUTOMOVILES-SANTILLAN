from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Catálogo público
    path('', views.lista_vehiculos, name='lista_vehiculos'),
    path('vehiculo/<int:pk>/', views.detalle_vehiculo, name='detalle_vehiculo'),

    # Panel de Configuración y Gestión (HTML Superusuario)
    path('panel/login/', views.panel_login, name='panel_login'),
    path('panel/logout/', views.panel_logout, name='panel_logout'),
    path('panel/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/vehiculo/nuevo/', views.panel_vehiculo_crear, name='panel_vehiculo_crear'),
    path('panel/vehiculo/<int:pk>/editar/', views.panel_vehiculo_editar, name='panel_vehiculo_editar'),
    path('panel/vehiculo/<int:pk>/eliminar/', views.panel_vehiculo_eliminar, name='panel_vehiculo_eliminar'),
    path('panel/vehiculo/<int:pk>/toggle/', views.panel_vehiculo_toggle_disponible, name='panel_vehiculo_toggle'),
    path('panel/vehiculo/<int:pk>/toggle-destacado/', views.panel_vehiculo_toggle_destacado, name='panel_vehiculo_toggle_destacado'),
    path('panel/imagen/<int:imagen_id>/eliminar/', views.panel_imagen_eliminar, name='panel_imagen_eliminar'),
]
