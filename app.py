import json
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Inicialización de la aplicación Flask
app = Flask(__name__)

# CORRECCIÓN FINAL: Habilitar CORS para permitir solicitudes desde AppSheet (cualquier origen, '*').
# Esto soluciona el problema de que AppSheet no recibe la respuesta JSON.
CORS(app, resources={r"/*": {"origins": "*"}}) 

# Función para generar números aleatorios
def generar_numeros_aleatorios(inferior, superior, cantidad):
    """Genera una cadena de números aleatorios sin repetición."""
    
    # 1. Validación de Rango Mínimo
    if inferior >= superior:
        return None # Indica un error de rango inválido
        
    # 2. Aseguramos que la cantidad no exceda el rango disponible
    rango_disponible = superior - inferior + 1
    if cantidad > rango_disponible:
        cantidad = rango_disponible
        
    # 3. Generación de los números sin repetición
    try:
        # random.sample es la forma más eficiente para obtener elementos únicos
        numeros = random.sample(range(inferior, superior + 1), cantidad)
    except ValueError:
        return None 
    
    # 4. Devuelve los números como una cadena separada por comas, ordenados para mejor lectura
    return ",".join(map(str, sorted(numeros))) 

@app.route('/generar', methods=['POST'])
def generar_numeros():
    """
    Endpoint que recibe los límites y la cantidad de AppSheet y devuelve los resultados 
    en un formato JSON compatible con el mapeo de columnas.
    """
    try:
        data = request.get_json()
        
        # 1. Extracción y Conversión de datos (usando claves en MINÚSCULAS)
        try:
            limite_inferior = int(data.get('limiteinferior', 0))
            limite_superior = int(data.get('limitesuperior', 0))
            cantidad = int(data.get('cantidad', 0))
        except (ValueError, TypeError):
            # Respuesta 400 si los datos son inválidos
            response = {
                "resultado": "",
                "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "codigo_status": "400",
                "mensaje_error": "Error 400: Los límites o la cantidad no son números válidos o están vacíos."
            }
            return jsonify(response), 400

        # 2. Generación de números
        resultado_str = generar_numeros_aleatorios(limite_inferior, limite_superior, cantidad)

        if resultado_str is None:
             # Respuesta 400 si el rango es inválido
             response = {
                "resultado": "",
                "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "codigo_status": "400",
                "mensaje_error": "Error 400: El límite inferior debe ser menor que el límite superior para generar números."
            }
             return jsonify(response), 400
            
        # 3. Respuesta exitosa (Código 200)
        response = {
            "resultado": resultado_str, # Clave en minúscula para mapeo de AppSheet
            "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Clave en minúscula
            "codigo_status": "200",
            "mensaje_error": "Operación completada exitosamente. Los números fueron generados y ordenados."
        }
        
        return jsonify(response), 200

    except Exception as e:
        # 4. Manejo de error interno (Error 500)
        response = {
            "resultado": "",
            "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigo_status": "500",
            "mensaje_error": f"Error 500: Fallo interno. Detalle: {str(e)}"
        }
        return jsonify(response), 500

# Esta línea solo se usa para probar localmente
if __name__ == '__main__':
    app.run(debug=True)