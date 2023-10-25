
from rest_framework_jwt.settings import api_settings

def custom_jwt_payload_handler(user_data):
    payload = {
        'nombre_usuario': user_data['nombre_usuario'],
        'correo': user_data['correo'],
        'contrasena': user_data['contrasena'],
        'estado': user_data['estado'],
    }
    return payload
