import requests
import datetime
import os
import sys

USERNAME = "weskerty" 
GIST_COUNT = 5
README_FILE = "README.md"
START = "<!-- GIST-LIST:START -->"
END = "<!-- GIST-LIST:END -->"

def fetch_gists():
    """Obtiene la lista de gists más recientes del usuario."""
    try:
        headers = {}
        # Si hay token de GitHub disponible, usarlo para evitar límites de rate
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        print(f"Obteniendo gists para el usuario: {USERNAME}")
        res = requests.get(f"https://api.github.com/users/{USERNAME}/gists", headers=headers)
        res.raise_for_status()
        
        gists = res.json()
        print(f"Se encontraron {len(gists)} gists")
        return gists[:GIST_COUNT]
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener gists: {e}")
        sys.exit(1)

def format_gists(gists):
    """Formatea los gists en markdown."""
    if not gists:
        return "No hay gists disponibles."
    
    lines = []
    for gist in gists:
        desc = gist.get("description") or "(Sin descripción)"
        url = gist.get("html_url", "#")
        created = gist.get("created_at", "")[:10] if gist.get("created_at") else "Fecha desconocida"
        
        # Obtener el primer archivo del gist para mostrar el lenguaje
        files = gist.get("files", {})
        language = ""
        if files:
            first_file = next(iter(files.values()))
            lang = first_file.get("language")
            if lang:
                language = f" `{lang}`"
        
        lines.append(f"- [{desc}]({url}){language} - {created}")
    
    return "\n".join(lines)

def update_readme(new_content):
    """Actualiza el README.md con el nuevo contenido de gists."""
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme = f.read()
    except FileNotFoundError:
        print(f"Archivo {README_FILE} no encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer {README_FILE}: {e}")
        sys.exit(1)

    start_idx = readme.find(START)
    end_idx = readme.find(END)
    
    if start_idx == -1:
        print(f"Marcador de inicio '{START}' no encontrado en {README_FILE}")
        print("Asegúrate de que el README tenga las etiquetas:")
        print(START)
        print(END)
        sys.exit(1)
    
    if end_idx == -1:
        print(f"Marcador de fin '{END}' no encontrado en {README_FILE}")
        sys.exit(1)

    # Crear el contenido actualizado
    updated = (
        readme[:start_idx + len(START)]
        + "\n" + new_content + "\n"
        + readme[end_idx:]
    )

    # Solo escribir si hay cambios
    if updated != readme:
        try:
            with open(README_FILE, "w", encoding="utf-8") as f:
                f.write(updated)
            print("✅ README.md actualizado con éxito.")
        except Exception as e:
            print(f"Error al escribir {README_FILE}: {e}")
            sys.exit(1)
    else:
        print("ℹ️ No hay cambios en la lista de gists.")

if __name__ == "__main__":
    print("🚀 Iniciando actualización de gists...")
    
    try:
        gists = fetch_gists()
        md_content = format_gists(gists)
        print(f"📝 Contenido generado:\n{md_content}")
        update_readme(md_content)
        print("✨ Proceso completado.")
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
