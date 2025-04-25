from django.contrib import admin

from Registrar_Presupuesto.views import gastos
from .models import Presupuesto, DetallePresupuesto, Categoria, Conceptos, Bancos, Responsables, Gasto, Saldos, Metas, Ingresos 

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mes', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre',)

admin.site.register(DetallePresupuesto)
admin.site.register(Categoria)
admin.site.register(Conceptos)
admin.site.register(Bancos)
admin.site.register(Responsables)
admin.site.register(Gasto)
admin.site.register(Saldos)
admin.site.register(Metas)
admin.site.register(Ingresos)



  

# Register your models here.
