import datetime
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Bancos, Categoria, DetallePresupuesto, Presupuesto
from django.http import JsonResponse
from Registrar_Presupuesto.models import Presupuesto, Categoria, Conceptos, Responsables, Bancos,Gasto, Ingresos, Saldos, Metas
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.contrib.humanize.templatetags.humanize import intcomma  # Para usar intcomma en la vista
from django.utils.safestring import mark_safe
from django.db.models import Sum, Max
import json
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout  # Corrige esta importación



@login_required
def lista_presupuestos(request):
    presupuestos = Presupuesto.objects.all()
    categorias = Categoria.objects.all()
    responsables = Responsables.objects.all()
    conceptos = Conceptos.objects.all()

    items = request.session.get('items_presupuesto', [])
    cabecera = request.session.get('cabecera_presupuesto', {})
    mostrar_modal = request.session.pop('presupuesto_guardado', False)

    total = sum(item.get('valor', 0) for item in items)

    return render(request, 'Registrar_Presupuesto/lista_presupuestos.html', {
        'presupuestos': presupuestos,
        'categorias': categorias,
        'responsables': responsables,
        'conceptos': conceptos,
        'items_presupuesto': items,
        'total_presupuesto': total,
        'cabecera_presupuesto': cabecera,
        'presupuesto_guardado': mostrar_modal,
    })
        
def ingresar_presupuesto(request):
    return render(request, 'Registrar_Presupuesto/ingresar_presupuesto.html')

def ingresar_saldo_cuentas(request):
    return render(request, 'Registrar_Presupuesto/ingresar_saldos.html')

def login(request):
    return render(request, 'Registrar_Presupuesto/login.html')

@login_required
def crear_presupuesto(request):
    return render(request, 'Registrar_Presupuesto/crear_presupuesto.html')

def definir_metas(request):
    return render(request, 'Registrar_Presupuesto/definir_metas.html')

def ver_metas(request):
        return render(request, 'Registrar_Presupuesto/ver_avance_metas.html')

@login_required
def capturar_cabecera_presupuesto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        mes = request.POST.get('mes')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        request.session['cabecera_presupuesto'] = {
            'nombre': nombre,
            'mes': mes,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
        request.session.modified = True

        return redirect('lista_presupuestos')
    return redirect('pagina_inicial')

@login_required
def pagina_inicial(request):
    mostrar_modal = request.session.pop('presupuesto_guardado', False)
    return render(request, 'Registrar_Presupuesto/Pagina_Inicial.html', {
        'presupuesto_guardado': mostrar_modal
    })


@login_required
def guardar_presupuesto(request):
    if request.method == 'POST':
        cabecera = request.session.get('cabecera_presupuesto')
        items = request.session.get('items_presupuesto', [])

        if not cabecera or not items:
            return redirect('pagina_inicial')

        try:
            mes_convertido = datetime.datetime.strptime(cabecera['mes'], "%Y-%m").date().replace(day=1)
        except ValueError:
            return redirect('pagina_inicial')

        total_presupuesto = sum(item.get('valor', 0) for item in items)

        presupuesto = Presupuesto.objects.create(
            nombre=cabecera['nombre'],
            mes=mes_convertido,
            fecha_inicio=cabecera['fecha_inicio'],
            fecha_fin=cabecera['fecha_fin'],
            total_presupuesto=total_presupuesto  # ✅ este es el nombre correcto del campo
        )

        for item in items:
            try:
                responsable = Responsables.objects.get(id=item['responsable_id'])
                categoria = Categoria.objects.get(id=item['categoria_id'])
                concepto = Conceptos.objects.get(id=item['concepto_id'])

                DetallePresupuesto.objects.create(
                    presupuesto=presupuesto,
                    concepto=concepto.nombre,
                    valor=item['valor'],
                    responsable=responsable,  # ✅ también corregido aquí
                    categoria=categoria,
                    observaciones=item.get('observaciones', '')
                )
            except Exception as e:
                print("Error al guardar item del presupuesto:", e)

        # Limpiar la sesión
        request.session['items_presupuesto'] = []
        request.session['cabecera_presupuesto'] = {}
        request.session['presupuesto_guardado'] = True
        request.session.modified = True

        return redirect('pagina_inicial')
    
    # En caso de que NO sea POST
    return redirect('pagina_inicial')



def agregar_al_carrito(request):
    if request.method == 'POST':
        concepto_id = request.POST.get('concepto_id')
        valor = float(request.POST.get('valor', 0))
        responsable_id = request.POST.get('responsable_id')
        observaciones = request.POST.get('observaciones')

        concepto = Conceptos.objects.get(id=concepto_id)
        responsable = Responsables.objects.get(id=responsable_id)
        categoria = concepto.categoria

        item = {
            'concepto_id': concepto.id,
            'nombre_concepto': concepto.nombre,
            'categoria_id': categoria.id,
            'categoria_nombre': categoria.nombre,
            'responsable_id': responsable.id,
            'responsable_nombre': responsable.nombre,
            'valor': valor,
            'observaciones': observaciones
        }

        # Guardar en sesión
        carrito = request.session.get('items_presupuesto', [])
        carrito.append(item)
        request.session['items_presupuesto'] = carrito
        request.session.modified = True

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@login_required
def total_presupuesto(request):
    items_presupuesto = request.session.get('items_presupuesto', [])
    return render(request, 'Registrar_Presupuesto/Total_Presupuesto.html', {
        'items_presupuesto': items_presupuesto
    })


@require_POST
def vaciar_carrito(request):
    try:
        request.session['items_presupuesto'] = []
        request.session.modified = True
    except Exception as e:
        print("Error al vaciar el carrito:", e)

    return redirect('total_presupuesto')


@require_POST
def eliminar_item_presupuesto(request, item_index):
    try:
        carrito = request.session.get('items_presupuesto', [])
        item_index = int(item_index)

        if 0 <= item_index < len(carrito):
            carrito.pop(item_index)
            request.session['items_presupuesto'] = carrito
            request.session.modified = True

    except Exception as e:
        print("Error al eliminar item del carrito:", e)

    return redirect('total_presupuesto')

def obtener_conceptos(request, categoria_id):
    conceptos = Conceptos.objects.filter(categoria_id=categoria_id).values('id', 'nombre')
    return JsonResponse(list(conceptos), safe=False)


def ingresos(request):
    return render(request, 'Registrar_Presupuesto/ingresos.html')

def gastos(request):
    return render(request, 'Registrar_Presupuesto/gastos.html') 

@login_required    
def gastos(request):
    if request.method == 'POST':
        presupuesto_id = request.POST.get('presupuesto')
        fecha = request.POST.get('fecha')
        categoria_id = request.POST.get('categoria')
        concepto_id = request.POST.get('concepto_id')
        responsable_id = request.POST.get('responsable_id')
        banco_id = request.POST.get('banco_id')
        valor = request.POST.get('valor')
        observaciones = request.POST.get('observaciones')

        print("📌 Datos recibidos:", presupuesto_id, fecha, categoria_id, concepto_id, responsable_id, banco_id, valor, observaciones)

        if all([fecha, categoria_id, concepto_id, responsable_id, banco_id, valor, presupuesto_id]):
            try:
                Gasto.objects.create(
                    presupuesto_id=presupuesto_id,
                    fecha=fecha,
                    categoria_id=categoria_id,
                    concepto_id=concepto_id,
                    responsable_id=responsable_id,
                    banco_id=banco_id,
                    valor=valor,
                    observaciones=observaciones
                )

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, "Gasto registrado exitosamente")
                    return redirect('gastos')

            except Exception as e:
                error_msg = f"Error al guardar el gasto: {str(e)}"
        else:
            error_msg = "Por favor, completa todos los campos obligatorios"

        # Si hay error
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        else:
            messages.error(request, error_msg)

    # GET: cargar datos para el formulario
    presupuesto = Presupuesto.objects.filter(estado=True)
    categorias = Categoria.objects.all()
    conceptos = Conceptos.objects.all()
    responsables = Responsables.objects.all()
    bancos = Bancos.objects.filter(estado=True)

    return render(request, 'Registrar_Presupuesto/gastos.html', {
        'presupuestos': presupuesto,
        'categorias': categorias,
        'conceptos': conceptos,
        'responsables': responsables,
        'bancos': bancos
    })


from django.http import JsonResponse

def ingresos(request):
    if request.method == 'POST':
        presupuesto_id = request.POST.get('presupuesto')
        fecha = request.POST.get('fecha')
        periodo = request.POST.get('periodo')
        responsable_id = request.POST.get('responsable_id')
        banco_id = request.POST.get('banco_id')
        valor = request.POST.get('valor')
        observaciones = request.POST.get('observaciones')

        print("📌 Datos recibidos:", presupuesto_id, fecha, periodo, responsable_id, banco_id, valor, observaciones)

        if all([fecha, periodo, responsable_id, banco_id, valor, presupuesto_id]):
            try:
                Ingresos.objects.create(
                    presupuesto_id=presupuesto_id,
                    fecha=fecha,
                    periodo=periodo,
                    responsable_id=responsable_id,
                    banco_id=banco_id,
                    valor=valor,
                    observaciones=observaciones
                )

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    messages.success(request, "Ingreso registrado exitosamente")
                    return redirect('ingresos')

            except Exception as e:
                error_msg = f"Error al guardar el ingreso: {str(e)}"
        else:
            error_msg = "Por favor, completa todos los campos obligatorios"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        else:
            messages.error(request, error_msg)

    # GET: Cargar datos para el formulario
    presupuestos = Presupuesto.objects.filter(estado=True)
    responsables = Responsables.objects.all()
    bancos = Bancos.objects.filter(estado=True)

    return render(request, 'Registrar_Presupuesto/ingresos.html', {
        'presupuestos': presupuestos,
        'responsables': responsables,
        'bancos': bancos
    })


def consultar_presupuesto(request):
    presupuesto_id = request.GET.get('presupuesto_id')
    categoria_id = request.GET.get('categoria')
    responsable_id = request.GET.get('responsable')

    presupuestos = Presupuesto.objects.filter(estado=True)
    categorias = Categoria.objects.all()
    responsables = Responsables.objects.all()

    items_presupuesto = []
    gastos_detalle = []
    total_presupuesto = 0
    total_gastos = 0
    porcentaje_cumplimiento = 0
    sobreejecutado = False
    grafico_categorias = []
    grafico_valores = []
    saldos_responsables = []
    saldos_bancos = []

    if presupuesto_id:
        filtros_detalle = {'presupuesto_id': presupuesto_id}
        filtros_gasto = {'presupuesto_id': presupuesto_id}
        filtros_ingreso = {'presupuesto_id': presupuesto_id}
        filtros_saldo = {'presupuesto_id': presupuesto_id}

        if categoria_id:
            filtros_detalle['categoria_id'] = categoria_id
            filtros_gasto['categoria_id'] = categoria_id
        if responsable_id:
            filtros_detalle['responsable_id'] = responsable_id
            filtros_gasto['responsable_id'] = responsable_id
            filtros_ingreso['responsable_id'] = responsable_id
            filtros_saldo['responsable_id'] = responsable_id

        # Aggregate presupuesto details for the table
        detalles_agregados_tabla = DetallePresupuesto.objects.filter(**filtros_detalle).values(
            'categoria__nombre',
            'responsable__nombre'
        ).annotate(
            valor=Sum('monto')
        )

        # Aggregate gastos for the table
        gastos_agregados_tabla = Gasto.objects.filter(**filtros_gasto).values(
            'categoria__nombre',
            'responsable__nombre'
        ).annotate(
            total_gasto=Sum('valor')
        )
        gastos_dict_tabla = {(g['categoria__nombre'], g['responsable__nombre']): g['total_gasto'] or 0 for g in gastos_agregados_tabla}

        for detalle in detalles_agregados_tabla:
            categoria_nombre = detalle['categoria__nombre']
            responsable_nombre = detalle['responsable__nombre']
            valor_presupuestado = detalle['valor'] or 0
            valor_gasto = gastos_dict_tabla.get((categoria_nombre, responsable_nombre), 0)
            diferencia = valor_presupuestado - valor_gasto

            items_presupuesto.append({
                'categoria_nombre': categoria_nombre,
                'responsable_nombre': responsable_nombre,
                'valor': valor_presupuestado,
                'valor_gasto': valor_gasto,
                'diferencia': diferencia,
                'resaltado': diferencia < 0
            })

        total_presupuesto = sum(item['valor'] for item in items_presupuesto)
        total_gastos = sum(item['valor_gasto'] for item in items_presupuesto)
        porcentaje_cumplimiento = (total_gastos / total_presupuesto * 100) if total_presupuesto > 0 else 0
        sobreejecutado = porcentaje_cumplimiento > 100

        # Data for the Distribución del Presupuesto por Categoría graph
        distribucion_data = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto_id)
        if categoria_id:
            distribucion_data = distribucion_data.filter(categoria_id=categoria_id)
        if responsable_id:
            distribucion_data = distribucion_data.filter(responsable_id=responsable_id)

        distribucion_agregada = distribucion_data.values('categoria__nombre').annotate(
            total_presupuestado=Sum('monto')
        ).order_by('categoria__nombre')

        grafico_categorias = [item['categoria__nombre'] for item in distribucion_agregada]
        grafico_valores = [item['total_presupuestado'] or 0 for item in distribucion_agregada]

        print("Categorías para el gráfico:", grafico_categorias)
        print("Valores para el gráfico:", grafico_valores)

        # Get detailed gastos
        gastos_detalle = Gasto.objects.filter(**filtros_gasto).select_related('categoria', 'concepto', 'responsable')

        # Saldos por responsable
        ingresos_por_responsable = Ingresos.objects.filter(**filtros_ingreso).values('responsable__nombre').annotate(
            total_ingresos=Sum('valor')
        )
        gastos_por_responsable = Gasto.objects.filter(**filtros_gasto).values('responsable__nombre').annotate(
            total_gastos=Sum('valor')
        )
        gastos_responsable_dict = {item['responsable__nombre']: item['total_gastos'] or 0 for item in gastos_por_responsable}

        saldos_responsables = []
        responsables_procesados = set()
        for ingreso in ingresos_por_responsable:
            responsable = ingreso['responsable__nombre']
            ingreso_total = ingreso['total_ingresos'] or 0
            gasto_total = gastos_responsable_dict.get(responsable, 0)
            saldo = ingreso_total - gasto_total
            saldos_responsables.append({
                'responsable': responsable,
                'ingresos': ingreso_total,
                'gastos': gasto_total,
                'saldo': saldo
            })
            responsables_procesados.add(responsable)

        # Añadir responsables con solo gastos o sin movimientos
        for gasto in gastos_por_responsable:
            responsable = gasto['responsable__nombre']
            if responsable not in responsables_procesados:
                saldos_responsables.append({
                    'responsable': responsable,
                    'ingresos': 0,
                    'gastos': gasto['total_gastos'] or 0,
                    'saldo': -(gasto['total_gastos'] or 0)
                })


        # Saldos por banco (latest saldo)
        subquery = Saldos.objects.filter(presupuesto_id=presupuesto_id).values('banco_id').annotate(
            ultima_fecha=Max('fecha')
        )
        saldos_banco_qs = Saldos.objects.filter(
            presupuesto_id=presupuesto_id,
            banco_id__in=subquery.values('banco_id'),
            fecha__in=subquery.values('ultima_fecha')
        ).select_related('banco', 'responsable') # Ensure 'responsable' is also selected

        saldos_bancos = []
        for saldo in saldos_banco_qs:
            saldos_bancos.append({
                'responsable': saldo.responsable.nombre,
                'banco': saldo.banco.nombre,
                'fecha': saldo.fecha,
                'saldo': saldo.saldo
            })

    context = {
        'presupuestos': presupuestos,
        'categorias': categorias,
        'responsables': responsables,
        'items_presupuesto': items_presupuesto,
        'total_presupuesto': total_presupuesto,
        'total_gastos': total_gastos,
        'porcentaje_cumplimiento': porcentaje_cumplimiento,
        'sobreejecutado': sobreejecutado,
        'grafico_categorias': grafico_categorias,
        'grafico_valores': grafico_valores,
        'gastos_detalle': gastos_detalle,
        'ingresos_resumen': saldos_responsables,
        'saldos_bancarios': saldos_bancos,
    }

    return render(request, 'Registrar_Presupuesto/consultar_presupuesto.html', context)

@login_required
def ingresar_item_presupuesto(request):
    # Obtener listas necesarias siempre
    presupuestos = Presupuesto.objects.filter(estado=True)
    categorias = Categoria.objects.all()
    responsables = Responsables.objects.all()

    # Obtener el presupuesto seleccionado desde GET o POST
    presupuesto_id = request.GET.get('presupuesto_id') or request.POST.get('presupuesto_id')
    presupuesto_seleccionado = None
    if presupuesto_id:
        try:
            presupuesto_seleccionado = Presupuesto.objects.get(id=presupuesto_id)
        except Presupuesto.DoesNotExist:
            messages.error(request, "El presupuesto seleccionado no existe.")
            return render(request, 'Registrar_Presupuesto/ingresar_Presupuesto.html', {
                'presupuestos': presupuestos,
                'categorias': categorias,
                'responsables': responsables,
                'presupuesto_seleccionado': None  # Limpiar la selección inválida
            })

    # Procesar formulario POST si hay datos
    if request.method == 'POST' and presupuesto_seleccionado:
        concepto_id = request.POST.get('concepto_id')
        responsable_id = request.POST.get('responsable_id')
        valor = request.POST.get('valor')
        observaciones = request.POST.get('observaciones')

        if concepto_id and responsable_id and valor:
            try:
                concepto = Conceptos.objects.get(id=concepto_id)
                responsable = Responsables.objects.get(id=responsable_id)

                # Obtener la categoría del concepto
                categoria = concepto.categoria

                DetallePresupuesto.objects.create(
                    presupuesto=presupuesto_seleccionado,
                    concepto=concepto,
                    categoria=categoria,
                    responsable=responsable,
                    valor=valor,
                    observaciones=observaciones
                )
                messages.success(request, "Ítem agregado al presupuesto exitosamente.")
                return redirect(request.path_info + f'?presupuesto_id={presupuesto_seleccionado.id}')  # Recargar con el presupuesto seleccionado
            except Conceptos.DoesNotExist:
                messages.error(request, "El concepto seleccionado no existe.")
            except Responsables.DoesNotExist:
                messages.error(request, "El responsable seleccionado no existe.")
            except ValueError:
                messages.error(request, "El valor debe ser un número válido.")
            except Exception as e:
                messages.error(request, f"Ocurrió un problema al guardar el ítem: {str(e)}")
        else:
            messages.error(request, "Por favor, complete todos los campos obligatorios.")

    # Renderizar siempre las listas en el contexto
    context = {
        'presupuestos': presupuestos,
        'categorias': categorias,
        'responsables': responsables,
        'presupuesto_seleccionado': presupuesto_seleccionado
    }

    return render(request, 'Registrar_Presupuesto/ingresar_Presupuesto.html', context)


@login_required
def ingresar_saldo_cuentas(request):
    presupuestos = Presupuesto.objects.filter(estado=True)
    bancos = Bancos.objects.filter(estado=True)
    responsables = Responsables.objects.all()

    context = {
        'presupuestos': presupuestos,
        'bancos': bancos,
        'responsables': responsables,
    }
    return render(request, 'Registrar_Presupuesto/ingresar_saldos.html', context)

@login_required
def guardar_saldos(request):
    if request.method == 'POST':
        presupuesto_id = request.POST.get('presupuesto_id')
        bancos_id = request.POST.get('bancos_id')
        responsable_id = request.POST.get('responsable_id')
        valor = request.POST.get('valor')
        fecha = request.POST.get('fecha')

        try:
            presupuesto = Presupuesto.objects.get(id=presupuesto_id)
            banco = Bancos.objects.get(id=bancos_id)
            responsable = Responsables.objects.get(id=responsable_id)

            Saldos.objects.create(
                presupuesto=presupuesto,
                banco=banco,
                responsable=responsable,
                saldo=valor,
                fecha=fecha,
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Saldo guardado exitosamente.")
                return redirect('ingresar_saldos')

        except Presupuesto.DoesNotExist:
            error_msg = "El presupuesto seleccionado no existe."
        except Bancos.DoesNotExist:
            error_msg = "El banco seleccionado no existe."
        except Responsables.DoesNotExist:
            error_msg = "El responsable seleccionado no existe."
        except ValueError:
            error_msg = "El valor debe ser un número válido."
        except Exception as e:
            error_msg = f"Ocurrió un problema al guardar el saldo: {str(e)}"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        else:
            messages.error(request, error_msg)

    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Método no permitido'})
        messages.error(request, "Método no válido.")
        return redirect('ingresar_saldos')

    # Si hubo un error (en modo no AJAX)
    presupuestos = Presupuesto.objects.filter(estado=True)
    bancos = Bancos.objects.filter(estado=True)
    responsables = Responsables.objects.all()
    context = {
        'presupuestos': presupuestos,
        'bancos': bancos,
        'responsables': responsables,
    }
    return render(request, 'Registrar_Presupuesto/ingresar_saldos.html', context)


def guardar_metas(request):
    try:
        categoria = Categoria.objects.get(id=11)
    except Categoria.DoesNotExist:
        messages.error(request, "La categoría no existe.")
        return redirect('definir_metas')

    if request.method == 'POST':
        print("🟢 POST recibido:")
        for key, value in request.POST.items():
            print(f"🔹 {key}: {value}")

        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        valor = request.POST.get('valor')
        fecha = request.POST.get('fecha')
        concepto_id = request.POST.get('concepto_id')
        categoria_id = request.POST.get('categoria_id')

        # Validación
        if not all([nombre, valor, fecha, concepto_id]):
            return JsonResponse({'success': False, 'message': 'Por favor, completa todos los campos obligatorios.'}, status=400)

        try:
            concepto = Conceptos.objects.get(id=concepto_id)
            categoria = Categoria.objects.get(id=categoria_id)

            nueva_meta = Metas.objects.create(
                Nombre=nombre,
                Descripcion=descripcion,
                Valor=valor,
                fecha_limite=fecha,
                Categoria=categoria,
                Conceptos=concepto
            )

            print(f"✅ Meta guardada: {nueva_meta}")
            return JsonResponse({'success': True, 'message': 'Meta guardada exitosamente.'})

        except Conceptos.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'El concepto seleccionado no existe.'}, status=404)
        except Exception as e:
            print(f"❌ Error al guardar la meta: {e}")
            return JsonResponse({'success': False, 'message': f'Error al guardar la meta: {str(e)}'}, status=500)

    # GET
    context = {
        'categoria': categoria,
        'conceptos': Conceptos.objects.all(),
    }
    return render(request, 'Registrar_Presupuesto/definir_metas.html', context)

def ver_avance_metas(request):
    # Obtener todas las metas y sus gastos asociados
    todas_las_metas = Metas.objects.all()
    # Obtener el ID de la meta seleccionada desde la URL

    meta_id = request.GET.get('meta_id')
    meta_seleccionada = None
    gastos_meta = []
    total_gastado = 0

    if meta_id:
        meta_seleccionada = get_object_or_404(Metas, id=meta_id)
        gastos_meta = Gasto.objects.filter(concepto=meta_seleccionada.Conceptos).order_by('-fecha')
        total_gastado = gastos_meta.aggregate(total=Sum('valor'))['total'] or 0

    context = {
        'todas_las_metas': todas_las_metas,
        'meta_seleccionada': meta_seleccionada,
        'gastos_meta': gastos_meta,
        'total_gastado': total_gastado,
    }
    
    return render(request, 'Registrar_Presupuesto/ver_avance_metas.html', context)



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Iniciar sesión del usuario
            return redirect('pagina_inicial')  # Redirigir al home o a la página inicial
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, 'Registrar_Presupuesto/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  

def ver_detalle_presupuesto (request):
    return render(request, 'Registrar_Presupuesto/total_presupuesto.html')