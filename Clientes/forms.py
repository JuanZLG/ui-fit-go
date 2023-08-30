from django import forms

class CrearClienteForm(forms.Form):
    documento = forms.CharField(label='Documento', max_length=15)
    nombres = forms.CharField(label='Nombres', max_length=50)
    apellidos = forms.CharField(label='Apellidos', max_length=50)
    celular = forms.CharField(label='Número de celular', max_length=10)
    barrio = forms.CharField(label='Barrio', max_length=50)
    direccion = forms.CharField(label='Dirección', max_length=100)
    estado = forms.IntegerField(label='Estado')
    id_municipio = forms.IntegerField(label='ID Municipio')
