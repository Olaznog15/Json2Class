# Json2Class

Este proyecto genera clases Python a partir de un archivo JSON predeterminado y permite crear nuevos JSONs usando esas clases.

## Estructura del Proyecto

- `default.json`: Archivo JSON predeterminado con el esquema base.
- `src/generator.py`: Script que genera la clase Python basada en `default.json`.
- `src/main.py`: Script principal que ejecuta el generador y demuestra el uso de la clase generada.
- `requirements.txt`: Dependencias del proyecto (vacío por ahora).

## Cómo Usar

1. Ejecuta el script principal:
   ```
   python src/main.py
   ```

Esto generará la clase en `src/generated_class.py` y creará un nuevo JSON basado en datos personalizados.

## Requisitos

- Python 3.12+
- Entorno virtual configurado en `.venv`
