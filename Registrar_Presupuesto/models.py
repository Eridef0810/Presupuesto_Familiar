from django.db import models
from datetime import date

class Presupuesto(models.Model):
    mes = models.DateField()
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField(default=date.today)
    fecha_fin = models.DateField(default=date.today)
    total_presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"  
  
    def __str__(self):
        return f"{self.nombre} - {self.mes} - {self.fecha_inicio} - {self.fecha_fin} - {self.total_presupuesto}"
    
class DetallePresupuesto(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='detalles')
    concepto = models.ForeignKey('Conceptos', on_delete=models.CASCADE, related_name='detalles')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_de_pago = models.DateField(default=date.today)    
    Categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='detalles')
    responsable = models.ForeignKey('Responsables', on_delete=models.CASCADE, related_name='detalles')
    observaciones = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = "Detalle de Presupuesto"
        verbose_name_plural = "Detalles de Presupuesto"

    def __str__(self):
        return f"{self.presupuesto.nombre} - {self.concepto.nombre} - {self.monto}"


    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre
    
class Conceptos (models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name='conceptos')
    class Meta:
        verbose_name = "Concepto"
        verbose_name_plural = "Conceptos"
    
    def __str__(self):
        return f"{self.nombre} - {self.categoria.nombre}"
    
class Bancos (models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    class Meta:
        verbose_name = "Banco"
        verbose_name_plural = "Bancos"
   
    def __str__(self):
        return f"{self.nombre}"
    
class Responsables(models.Model):
    nombre = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
    
    
    def __str__(self):
        return f"{self.nombre}"
    
class Gasto(models.Model):
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    concepto = models.ForeignKey(Conceptos, on_delete=models.CASCADE)
    responsable = models.ForeignKey(Responsables, on_delete=models.CASCADE)
    banco = models.ForeignKey(Bancos, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='gastos', default=1)

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"

    def __str__(self):
        return f"{self.concepto.nombre} - {self.valor}"

class Ingresos (models.Model):
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    responsable = models.ForeignKey(Responsables, on_delete=models.CASCADE)
    banco = models.ForeignKey(Bancos, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='ingresos', default=1)
    periodo = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"

    def __str__(self):
        return f"{self.concepto.nombre} - {self.valor}"
    
class Saldos (models.Model):
    banco = models.ForeignKey(Bancos, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    responsable = models.ForeignKey(Responsables, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='saldos', default=1)

    class Meta:
        verbose_name = "Saldo"
        verbose_name_plural = "Saldos"

    def __str__(self):
        return f"{self.banco.nombre} - {self.saldo}"
    

class Metas (models.Model):
    Categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    Conceptos = models.ForeignKey(Conceptos, on_delete=models.CASCADE)
    Nombre = models.CharField(max_length=100)
    Descripcion = models.TextField()
    Valor = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_limite = models.DateField()
    
    class Meta:
        verbose_name = "Meta"
        verbose_name_plural = "Metas"  
        
    def __str__(self):
        return f"{self.Nombre} - {self.Valor} - {self.fecha_limite}"    