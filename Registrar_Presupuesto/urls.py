from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),  # Ruta para login
    path('pagina-inicial/', views.pagina_inicial, name='pagina_inicial'),  # Redirigir a la página inicial tras loguearse
    path('logout/', views.logout, name='logout'),  # Ruta para cerrar sesión (más adelante)
    
   

    # Presupuesto
    path('lista_presupuestos/', views.lista_presupuestos, name='lista_presupuestos'),
    path('guardar_presupuesto/', views.guardar_presupuesto, name='guardar_presupuesto'),
    path('crear_presupuesto/', views.crear_presupuesto, name='crear_presupuesto'),
    path('agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('total-presupuesto/', views.total_presupuesto, name='total_presupuesto'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('eliminar_item/<int:item_index>/', views.eliminar_item_presupuesto, name='eliminar_item_presupuesto'),
    path('capturar_cabecera/', views.capturar_cabecera_presupuesto, name='capturar_cabecera_presupuesto'),
    path('ingresos/', views.ingresos, name='ingresos'),
    path('gastos/', views.gastos, name='gastos'),
    path('consultar_presupuesto/', views.consultar_presupuesto, name='consultar_presupuesto'),
    path('ingresar_presupuesto/', views.ingresar_item_presupuesto, name='ingresar_item_presupuesto'),
    path('ingresar_presupuesto/', views.ingresar_presupuesto, name='ingresar_presupuesto'),
    path('ingresar_saldos/', views.ingresar_saldo_cuentas, name='ingresar_saldos'),
    path('guardar_saldo/', views.guardar_saldos, name='guardar_saldos'),
    path('definir_metas/', views.definir_metas, name='definir_metas'),
    path('guardar_metas/', views.guardar_metas, name='guardar_metas'),
    path('avance_metas/', views.ver_avance_metas, name='ver_avance_metas'),
    path('pagina-inicial/', views.pagina_inicial, name='pagina_inicial'),
    path('detalle_presupuesto/', views.ver_detalle_presupuesto, name='detalle_presupuesto'),
    path('obtener-eventos/<int:presupuesto_id>/', views.obtener_eventos_presupuesto, name='obtener_eventos'),
    path('guardar_gasto/', views.guardar_gasto, name='guardar_gasto'),
    path('exportar-presupuesto/', views.exportar_presupuesto, name='exportar_presupuesto'),

    # API AJAX
    path('conceptos/<int:categoria_id>/', views.obtener_conceptos, name='obtener_conceptos'),
    path('api/conceptos/<int:categoria_id>/', views.obtener_conceptos, name='api_conceptos'),
    path('meta/<int:meta_id>/avance/', views.ver_avance_metas, name='ver_avance_metas'),  
    path('obtener_detalle_presupuesto/<int:detalle_id>/', views.obtener_detalle_presupuesto, name='obtener_detalle_presupuesto'),

]




