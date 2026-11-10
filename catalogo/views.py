from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch, Q
from .models import Vehiculo, VehiculoImagen
from .forms import VehiculoForm, PanelLoginForm
from .utils import convertir_imagen_a_webp


# ==========================================
# VISTAS PÚBLICAS DEL CATÁLOGO
# ==========================================

def lista_vehiculos(request):
    """
    Vista principal del catálogo para clientes.
    Muestra solo vehículos disponibles y permite filtrar por categoría,
    ver solo vehículos destacados, o buscar por texto.
    """
    categoria_seleccionada = request.GET.get('categoria', '').strip()
    busqueda = request.GET.get('q', '').strip()

    vehiculos = Vehiculo.objects.filter(disponible=True).prefetch_related(
        Prefetch('imagenes', queryset=VehiculoImagen.objects.order_by('orden', 'id'))
    )

    # Filtro especial por "Destacados"
    es_destacados = categoria_seleccionada.lower() in ('destacados', 'destacado')

    if es_destacados:
        vehiculos = vehiculos.filter(destacado=True)
    elif categoria_seleccionada:
        vehiculos = vehiculos.filter(categoria=categoria_seleccionada)

    if busqueda:
        q_filtros = (
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(motor__icontains=busqueda) |
            Q(categoria__icontains=busqueda) |
            Q(combustible__icontains=busqueda)
        )
        if busqueda.isdigit():
            q_filtros |= Q(anio=int(busqueda))
        vehiculos = vehiculos.filter(q_filtros)

    categorias = Vehiculo.Categoria.choices
    # Contar únicamente los vehículos visibles/disponibles para venta
    total_disponibles = Vehiculo.objects.filter(disponible=True).count()
    total_destacados = Vehiculo.objects.filter(disponible=True, destacado=True).count()
    total_resultados = vehiculos.count()

    context = {
        'vehiculos': vehiculos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'es_destacados': es_destacados,
        'total_destacados': total_destacados,
        'busqueda': busqueda,
        'total_vehiculos': total_disponibles,
        'total_resultados': total_resultados,
    }
    return render(request, 'catalogo/lista_vehiculos.html', context)


def detalle_vehiculo(request, pk):
    """
    Vista de detalle para un vehículo específico con carrusel de fotos.
    """
    vehiculo = get_object_or_404(
        Vehiculo.objects.prefetch_related(
            Prefetch('imagenes', queryset=VehiculoImagen.objects.order_by('orden', 'id'))
        ),
        pk=pk
    )

    relacionados = Vehiculo.objects.filter(
        categoria=vehiculo.categoria,
        disponible=True
    ).exclude(pk=vehiculo.pk)[:3].prefetch_related('imagenes')

    context = {
        'vehiculo': vehiculo,
        'imagenes': vehiculo.imagenes.all(),
        'relacionados': relacionados,
    }
    return render(request, 'catalogo/detalle_vehiculo.html', context)


# ==========================================
# PANEL DE ADMINISTRACIÓN / CONFIGURACIÓN HTML
# ==========================================

def es_administrador(user):
    """Valida que el usuario esté autenticado y sea superusuario o staff."""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def panel_login(request):
    """
    Pantalla de inicio de sesión HTML personalizada para el panel de administración.
    Valida credenciales de superusuario/staff.
    """
    if es_administrador(request.user):
        return redirect('catalogo:panel_dashboard')

    if request.method == 'POST':
        form = PanelLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser or user.is_staff:
                login(request, user)
                messages.success(request, f"¡Bienvenido al Panel de Configuración, {user.username}!")
                return redirect('catalogo:panel_dashboard')
            else:
                messages.error(request, "Acceso restringido: Se requieren permisos de superusuario o administrador.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Verifique sus credenciales.")
    else:
        form = PanelLoginForm()

    return render(request, 'panel/login.html', {'form': form})


def panel_logout(request):
    """Cierra la sesión del administrador y redirige al catálogo."""
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('catalogo:lista_vehiculos')


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_dashboard(request):
    """
    Panel central de configuración:
    Muestra la lista de TODOS los vehículos para gestionarlos, editarlos o eliminarlos.
    """
    busqueda = request.GET.get('q', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()

    vehiculos = Vehiculo.objects.all().prefetch_related('imagenes').order_by('-creado_el')

    if busqueda:
        vehiculos = vehiculos.filter(
            Q(marca__icontains=busqueda) |
            Q(modelo__icontains=busqueda) |
            Q(motor__icontains=busqueda)
        )

    if categoria_filtro:
        if categoria_filtro == 'destacados':
            vehiculos = vehiculos.filter(destacado=True)
        else:
            vehiculos = vehiculos.filter(categoria=categoria_filtro)

    total_total = Vehiculo.objects.count()
    total_disponibles = Vehiculo.objects.filter(disponible=True).count()
    total_destacados = Vehiculo.objects.filter(destacado=True).count()
    total_pausados = total_total - total_disponibles

    context = {
        'vehiculos': vehiculos,
        'total_total': total_total,
        'total_disponibles': total_disponibles,
        'total_destacados': total_destacados,
        'total_pausados': total_pausados,
        'categorias': Vehiculo.Categoria.choices,
        'busqueda': busqueda,
        'categoria_filtro': categoria_filtro,
    }
    return render(request, 'panel/dashboard.html', context)


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_vehiculo_crear(request):
    """
    Formulario para dar de alta un nuevo vehículo con carga múltiple de hasta 20 fotos.
    """
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        archivos = request.FILES.getlist('imagenes')

        if form.is_valid():
            vehiculo = form.save()

            # Guardar fotos convertidas automáticamente a WebP (hasta un máximo de 20)
            contador_fotos = 0
            for i, archivo in enumerate(archivos[:20], start=1):
                archivo_webp = convertir_imagen_a_webp(archivo)
                VehiculoImagen.objects.create(
                    vehiculo=vehiculo,
                    imagen=archivo_webp,
                    orden=i
                )
                contador_fotos += 1

            if len(archivos) > 20:
                messages.warning(request, f"Vehículo creado. Se guardaron las primeras 20 fotos permitidas (se ignoraron {len(archivos) - 20}).")
            else:
                messages.success(request, f"¡Vehículo '{vehiculo.marca} {vehiculo.modelo}' cargado con éxito ({contador_fotos} fotos adjuntas)!")

            return redirect('catalogo:panel_dashboard')
    else:
        form = VehiculoForm()

    return render(request, 'panel/vehiculo_form.html', {
        'form': form,
        'titulo': 'Cargar Nuevo Vehículo',
        'subtitulo': 'Completa la ficha técnica y sube hasta 20 fotos del vehículo.',
        'vehiculo': None,
    })


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_vehiculo_editar(request, pk):
    """
    Formulario para editar un vehículo existente y administrar su galería de fotos.
    """
    vehiculo = get_object_or_404(Vehiculo.objects.prefetch_related('imagenes'), pk=pk)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        archivos = request.FILES.getlist('imagenes')

        if form.is_valid():
            vehiculo = form.save()

            # Comprobar cuántas fotos tiene actualmente
            fotos_actuales = vehiculo.imagenes.count()
            cupo_disponible = max(0, 20 - fotos_actuales)

            if archivos and cupo_disponible > 0:
                for i, archivo in enumerate(archivos[:cupo_disponible], start=fotos_actuales + 1):
                    archivo_webp = convertir_imagen_a_webp(archivo)
                    VehiculoImagen.objects.create(
                        vehiculo=vehiculo,
                        imagen=archivo_webp,
                        orden=i
                    )
                messages.success(request, f"Vehículo actualizado y se añadieron {min(len(archivos), cupo_disponible)} nuevas fotos optimizadas en WebP.")
            elif archivos and cupo_disponible == 0:
                messages.warning(request, "El vehículo ya alcanzó el límite máximo de 20 fotos. Elimina alguna para subir nuevas.")
            else:
                messages.success(request, f"Vehículo '{vehiculo.marca} {vehiculo.modelo}' actualizado exitosamente.")

            return redirect('catalogo:panel_dashboard')
    else:
        form = VehiculoForm(instance=vehiculo)

    return render(request, 'panel/vehiculo_form.html', {
        'form': form,
        'titulo': f'Editar {vehiculo.marca} {vehiculo.modelo}',
        'subtitulo': f'Modifica los datos o gestiona las fotos de la unidad #{vehiculo.pk}.',
        'vehiculo': vehiculo,
        'imagenes': vehiculo.imagenes.all().order_by('orden', 'id'),
        'cupo_fotos': max(0, 20 - vehiculo.imagenes.count()),
    })


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_vehiculo_eliminar(request, pk):
    """
    Elimina un vehículo y todas sus fotos asociadas.
    Soporta confirmación GET y acción POST.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=pk)

    if request.method == 'POST':
        nombre_auto = f"{vehiculo.marca} {vehiculo.modelo} ({vehiculo.anio})"
        vehiculo.delete()
        messages.success(request, f"El vehículo '{nombre_auto}' fue eliminado definitivamente del catálogo.")
        return redirect('catalogo:panel_dashboard')

    return render(request, 'panel/vehiculo_confirm_delete.html', {'vehiculo': vehiculo})


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_imagen_eliminar(request, imagen_id):
    """
    Elimina una fotografía individual de la galería de un vehículo.
    """
    imagen = get_object_or_404(VehiculoImagen, pk=imagen_id)
    vehiculo_pk = imagen.vehiculo.pk

    if request.method == 'POST':
        imagen.delete()
        messages.success(request, "Foto eliminada correctamente.")

    return redirect('catalogo:panel_vehiculo_editar', pk=vehiculo_pk)


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_vehiculo_toggle_disponible(request, pk):
    """
    Alterna rápidamente la disponibilidad de un vehículo (Disponible <-> Pausado).
    """
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    vehiculo.disponible = not vehiculo.disponible
    vehiculo.save(update_fields=['disponible'])

    estado = "activado (visible en catálogo)" if vehiculo.disponible else "pausado (oculto en catálogo)"
    messages.info(request, f"{vehiculo.marca} {vehiculo.modelo} ahora está {estado}.")
    return redirect('catalogo:panel_dashboard')


@user_passes_test(es_administrador, login_url='catalogo:panel_login')
def panel_vehiculo_toggle_destacado(request, pk):
    """
    Alterna rápidamente la condición de destacado de un vehículo con un solo clic.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    vehiculo.destacado = not vehiculo.destacado
    vehiculo.save(update_fields=['destacado'])

    estado = "marcado como DESTACADO ⭐" if vehiculo.destacado else "removido de destacados"
    messages.info(request, f"{vehiculo.marca} {vehiculo.modelo} ahora está {estado}.")
    return redirect('catalogo:panel_dashboard')
