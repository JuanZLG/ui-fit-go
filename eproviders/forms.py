from django import forms

class CrearProveedorForm (forms.Form):
    nombre_proveedor = forms.CharField(label='Nombre del proveedor',max_length=65)
    telefono = forms.CharField(label='# de celular',max_length=10)
    correo = forms.CharField(label='Correo electrónico',max_length=65)