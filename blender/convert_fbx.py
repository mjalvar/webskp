import bpy
import sys

# Captura corregida de rutas individuales
args = sys.argv[sys.argv.index("--") + 1:]
archivo_fbx = args[0]  # Entrada
archivo_glb = args[1]  # Salida

# 1. Limpiar el cubo, luz y cámara iniciales de Blender
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Importar el archivo FBX generado
print(f"Importando FBX desde la ruta: {archivo_fbx}")
bpy.ops.import_scene.fbx(filepath=archivo_fbx)

# 3. Forzar a Blender a empaquetar de forma obligatoria todas las texturas
bpy.ops.file.pack_all()

# 4. Exportar al formato binario .glb ideal para el Meta Quest Browser
# (Se removió 'export_colors' para compatibilidad nativa con Blender 4.3+)
print(f"Exportando GLB para Meta Quest 3 en: {archivo_glb}")
bpy.ops.export_scene.gltf(
    filepath=archivo_glb,
    export_format='GLB',
    export_materials='EXPORT' # Conserva materiales y texturas
)

print("[ÉXITO] ¡Archivo .glb creado con texturas y colores completos!")
