import json
import random
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS # Importación necesaria para el despliegue

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Habilitar CORS para permitir solicitudes desde AppSheet o cualquier otro origen
CORS(app)

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
    # random.sample es la forma más eficiente de obtener 'cantidad' elementos únicos
    try:
        numeros = random.sample(range(inferior, superior + 1), cantidad)
    except ValueError:
        # Esto sucede si el rango es 0 o negativo, aunque la validación 1 ya debería haberlo capturado
        return None 
    
    # 4. Devuelve los números como una cadena separada por comas
    return ",".join(map(str, sorted(numeros))) # Usamos sorted() para que los números siempre salgan ordenados

@app.route('/generar', methods=['POST'])
def generar_numeros():
    """
    Endpoint que recibe los límites y la cantidad de AppSheet (claves en minúsculas) 
    y devuelve los resultados, también con claves en minúsculas, como AppSheet lo requiere.
    """
    try:
        data = request.get_json()
        
        # 1. Extracción y Conversión de datos (usando claves en MINÚSCULAS)
        try:
            # AppSheet envía TEXTO, lo convertimos a INT. Usamos .get() para evitar errores si la clave no existe.
            limite_inferior = int(data.get('limiteinferior', 0))
            limite_superior = int(data.get('limitesuperior', 0))
            cantidad = int(data.get('cantidad', 0))
        except (ValueError, TypeError):
            # Error si los datos enviados no son números válidos
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
             # Error si el límite inferior es mayor o igual al superior
             response = {
                "resultado": "",
                "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "codigo_status": "400",
                "mensaje_error": "Error 400: El límite inferior debe ser menor que el límite superior para generar números."
            }
             return jsonify(response), 400
            
        # 3. Respuesta exitosa con claves en MINÚSCULAS para AppSheet
        response = {
            "resultado": resultado_str,
            "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigo_status": "200",
            "mensaje_error": "Transaccion completada exitosamente. Los números fueron generados y ordenados."
        }
        
        return jsonify(response), 200

    except Exception as e:
        # 4. Manejo de error interno (Error 500)
        response = {
            "resultado": "",
            "fechageneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigo_status": "500",
            "mensaje_error": f"Error 500: Fallo interno. Revise el código de Python. Detalle: {str(e)}"
        }
        return jsonify(response), 500

# Esta línea solo se usa para probar localmente (no se ejecuta en Render)
if __name__ == '__main__':
    app.run(debug=True)
