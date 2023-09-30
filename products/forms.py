from django import forms
from .models import Categorias, Marcas

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['nombre_categoria']
    
    def clean(self):
        cleaned_data = super().clean()
        nombre_categoria = cleaned_data.get('nombre_categoria')
        if not nombre_categoria:
            raise forms.ValidationError("El campo 'nombre_categoria' es obligatorio.")

class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marcas
        fields = ['nombre_marca']
    
    def clean(self):
        cleaned_data = super().clean()
        nombre_marca = cleaned_data.get('nombre_marca')
        if not nombre_marca:
            raise forms.ValidationError("El campo 'nombre_categoria' es obligatorio.")
