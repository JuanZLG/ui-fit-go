# from django.contrib.auth.backends import ModelBackend
# from .models import Usuarios

# class CustomAuthBackend(ModelBackend):
#     def authenticate(self, request, correo=None, contrasena=None, **kwargs):
#         try:
#             user = Usuarios.objects.get(correo=correo)
#             if user.check_password(contrasena) and user.estado:
#                 return user
#         except Usuarios.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return Usuarios.objects.get(pk=user_id)
#         except Usuarios.DoesNotExist:
#             return None
