import requests
import datetime
import os
import sys
import time

USERNAME = "weskerty"
GIST_COUNT = 5
README_FILE = "README.md"
START = "<!-- GIST-LIST:START -->"
END = "<!-- GIST-LIST:END -->"

def fetch_gists():
    """Obtiene la lista de gists más recientes del usuario."""
    try:
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': f'GitHub-Actions-Bot/1.0 ({USERNAME})'
        }
        
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            headers['Authorization'] = f'Bearer {github_token}'
        
        print(f"Obteniendo gists para el usuario: {USERNAME}")
        
        url = f"https://api.github.com/users/{USERNAME}/gists"
        
        for attempt in range(3):
            try:
                res = requests.get(url, headers=headers, timeout=30)
                
                if res.status_code == 403:
                    rate_limit_remaining = res.headers.get('X-RateLimit-Remaining', 'unknown')
                    rate_limit_reset = res.headers.get('X-RateLimit-Reset', 'unknown')
                    print(f"Rate limit - Remaining: {rate_limit_remaining}, Reset: {rate_limit_reset}")
                    
                    if attempt < 2:
                        print(f"Intento {attempt + 1} falló con 403, esperando 60 segundos...")
                        time.sleep(60)
                        continue
                    else:
                        print("Error 403: Acceso denegado. Verifica que:")
                        print("1. Los gists sean públicos")
                        print("2. El token tenga los permisos correctos")
                        print("3. No hayas excedido el rate limit")
                        return []
                
                elif res.status_code == 404:
                    print(f"Usuario {USERNAME} no encontrado o no tiene gists públicos")
                    return []
                
                res.raise_for_status()
                
                gists = res.json()
                if not isinstance(gists, list):
                    print("Respuesta inesperada de la API")
                    return []
                
                public_gists = [g for g in gists if g.get('public', True)]
                
                print(f"Se encontraron {len(public_gists)} gists públicos")
                return public_gists[:GIST_COUNT]
                
            except requests.exceptions.Timeout:
                print(f"Timeout en intento {attempt + 1}")
                if attempt < 2:
                    time.sleep(10)
                    continue
                else:
                    raise
            except requests.exceptions.RequestException as e:
                print(f"Error en intento {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(10)
                    continue
                else:
                    raise
        
        return []
        
    except Exception as e:
        print(f"Error al obtener gists: {e}")
        return []

def format_gists(gists):
    """Formatea los gists en markdown."""
    if not gists:
        return "No hay gists públicos disponibles."
    
    lines = []
    for gist in gists:
        try:
            desc = gist.get("description") or "(Sin descripción)"
            url = gist.get("html_url", "#")
            created_at = gist.get("created_at", "")
            
            if created_at:
                try:
                    date_obj = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created = date_obj.strftime("%Y-%m-%d")
                except:
                    created = created_at[:10] if len(created_at) >= 10 else "Fecha desconocida"
            else:
                created = "Fecha desconocida"
            
            files = gist.get("files", {})
            language = ""
            if files:
                first_file = next(iter(files.values()), {})
                lang = first_file.get("language")
                if lang:
                    language = f" `{lang}`"
            
            lines.append(f"- [{desc}]({url}){language} - {created}")
            
        except Exception as e:
            print(f"Error procesando gist: {e}")
            continue
    
    return "\n".join(lines) if lines else "No se pudieron procesar los gists."

def update_readme(new_content):
    """Actualiza el README.md con el nuevo contenido de gists."""
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            readme = f.read()
    except FileNotFoundError:
        print(f"Archivo {README_FILE} no encontrado.")
        return False
    except Exception as e:
        print(f"Error al leer {README_FILE}: {e}")
        return False

    start_idx = readme.find(START)
    end_idx = readme.find(END)
    
    if start_idx == -1 or end_idx == -1:
        print(f"Marcadores no encontrados en {README_FILE}")
        print("Asegúrate de que el README tenga:")
        print(START)
        print(END)
        return False

    updated = (
        readme[:start_idx + len(START)]
        + "\n" + new_content + "\n"
        + readme[end_idx:]
    )

    if updated != readme:
        try:
            with open(README_FILE, "w", encoding="utf-8") as f:
                f.write(updated)
            print("✅ README.md actualizado con éxito.")
            return True
        except Exception as e:
            print(f"Error al escribir {README_FILE}: {e}")
            return False
    else:
        print("ℹ️ No hay cambios en la lista de gists.")
        return True

if __name__ == "__main__":
    print("🚀 Iniciando actualización de gists...")
    
    try:
        gists = fetch_gists()
        md_content = format_gists(gists)
        print(f"📝 Contenido generado:\n{md_content}")
        
        if update_readme(md_content):
            print("✨ Proceso completado exitosamente.")
            sys.exit(0)
        else:
            print("❌ Falló la actualización del README.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
