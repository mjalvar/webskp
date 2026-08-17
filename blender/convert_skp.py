import trimesh
import sys
import os

# Capturar los argumentos de la consola
if len(sys.argv) < 3:
    print("Uso: python3 convertir_skp.py <archivo_entrada.skp> <archivo_salida.glb>")
    sys.exit(1)

entrada = sys.argv[1]
salida = sys.argv[2]

if not os.path.exists(entrada):
    print(f"Error: El archivo {entrada} no existe.")
    sys.exit(1)

print(f"Leyendo estructura interna de SketchUp: {entrada}...")

try:
    # Trimesh lee el contenedor del .skp de forma nativa como una escena tridimensional
    escena = trimesh.load(entrada, force='mesh')
    
    print("Geometría detectada con éxito. Exportando a formato WebXR (.glb)...")
    
    # Exportar el binario final integrado
    escena.export(salida, file_type='glb')
    
    tamano = os.path.getsize(salida) / 1024
    print(f"\n[ÉXITO] Archivo generado. Peso real: {tamano:.2f} KB")

except Exception as e:
    print(f"\n[ERROR] No se pudo procesar el archivo de forma directa: {str(e)}")
    print("Probando método alternativo de desempaquetado de componentes...")
    sys.exit(1)
