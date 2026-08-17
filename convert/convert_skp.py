#!/usr/bin/env python3
"""convert_skp.py

Convierte un archivo .skp a .glb usando `wine skp2gltf.exe` y `gltf-pipeline`.

Uso:
  python3 convert_skp.py archivo_entrada.skp

Opciones útiles:
  --workdir DIR       Directorio temporal de salida (por defecto: workdir)
  --profile NAME      Perfil para skp2gltf (por defecto: quest3)
  --skp2gltf PATH     Ruta a skp2gltf.exe (si no está en el mismo directorio)
  --gltf-pipeline CMD Comando para gltf-pipeline (por defecto: gltf-pipeline)
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_executable(name, fallback_path=None):
    if fallback_path:
        p = Path(fallback_path)
        if p.exists():
            return str(p)
    w = shutil.which(name)
    return w


def main():
    parser = argparse.ArgumentParser(description='Convert .skp -> .glb via wine + gltf-pipeline')
    parser.add_argument('input', help='Archivo .skp de entrada')
    parser.add_argument('--workdir', default='workdir', help='Directorio temporal de trabajo')
    parser.add_argument('--profile', default='quest3', help='Perfil para skp2gltf.exe')
    parser.add_argument('--skp2gltf', default=None, help='Ruta a skp2gltf.exe')
    parser.add_argument('--gltf-pipeline', dest='gltf_pipeline', default='gltf-pipeline', help='Comando gltf-pipeline')
    args = parser.parse_args()

    inp = Path(args.input).resolve()
    if not inp.exists():
        print(f"Error: archivo de entrada no encontrado: {inp}")
        sys.exit(2)

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    # Localizar skp2gltf.exe
    script_dir = Path(__file__).resolve().parent
    skp2gltf_path = None
    if args.skp2gltf:
        skp2gltf_path = find_executable(None, args.skp2gltf)
    if not skp2gltf_path:
        candidate = script_dir / 'skp2gltf.exe'
        if candidate.exists():
            skp2gltf_path = str(candidate)
    if not skp2gltf_path:
        skp2gltf_path = find_executable('skp2gltf.exe') or find_executable('skp2gltf')

    if not skp2gltf_path:
        print("Error: no se encontró 'skp2gltf.exe'. Colócalo junto al script o pásalo con --skp2gltf")
        sys.exit(3)

    print(f"Usando skp2gltf: {skp2gltf_path}")

    # Ejecutar via wine
    cmd = ['wine', skp2gltf_path, str(inp), str(workdir)+'/', args.profile]
    print('Ejecutando:', ' '.join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"Error: skp2gltf devolvió código {r.returncode}")
        sys.exit(r.returncode)

    generated_gltf = workdir / f"{args.profile}.gltf"
    if not generated_gltf.exists():
        print(f"Error: no se generó {generated_gltf}")
        sys.exit(4)

    # Determinar salida final
    out_glb = inp.with_suffix('.glb')

    # Ejecutar gltf-pipeline
    gp_cmd = None
    if shutil.which(args.gltf_pipeline):
        gp_cmd = [args.gltf_pipeline, '-i', str(generated_gltf), '-o', str(out_glb)]
    else:
        # usar npx como fallback si no hay instalación global
        if shutil.which('npx'):
            gp_cmd = ['npx', 'gltf-pipeline', '-i', str(generated_gltf), '-o', str(out_glb)]

    if gp_cmd is None:
        print("Error: no se encontró 'gltf-pipeline' ni 'npx'. Instala gltf-pipeline (npm) o añade a PATH.")
        sys.exit(5)

    print('Ejecutando:', ' '.join(gp_cmd))
    r2 = subprocess.run(gp_cmd)
    if r2.returncode != 0:
        print(f"Error: gltf-pipeline devolvió código {r2.returncode}")
        sys.exit(r2.returncode)

    if out_glb.exists():
        size_kb = out_glb.stat().st_size / 1024
        print(f"Éxito: generado {out_glb} ({size_kb:.2f} KB)")
        return 0
    else:
        print("Error: no se generó el .glb final")
        return 6


if __name__ == '__main__':
    sys.exit(main() or 0)
