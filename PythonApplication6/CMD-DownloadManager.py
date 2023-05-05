import requests
import time
import os
import re
from tqdm import tqdm
from urllib.parse import urlparse


def solicitar_datos_usuario():
    url = input("Introduce la URL del archivo: ")
    nombre = input("Introduce el nombre del archivo: ")
    ubicacion = input("Introduce la ubicación donde se guardará el archivo: ")
    return url, nombre, ubicacion


def validar_datos(url, ubicacion):
    if not validar_url(url):
        print('La URL no es válida.')
        return False

    if not validar_ubicacion(ubicacion):
        print('La ubicación no es válida.')
        return False

    return True


def validar_url(url):
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False


def validar_ubicacion(ubicacion):
    return os.path.isdir(ubicacion) and os.access(ubicacion, os.W_OK)


def descargar_archivo(url, nombre, ubicacion):
    try:
        respuesta = requests.get(url, stream=True, verify=True)
        respuesta.raise_for_status()

        if respuesta.status_code == 200:
            extension = url.split(".")[-1]
            ruta_archivo = f"{ubicacion}/{nombre}.{extension}"
            with open(ruta_archivo, "wb") as archivo:
                tamano_archivo = int(respuesta.headers.get("content-length", 0))
                progreso = tqdm(total=tamano_archivo, unit="B", unit_scale=True)
                tiempo_inicial = time.time()

                for datos in respuesta.iter_content(chunk_size=1024):
                    archivo.write(datos)
                    progreso.update(len(datos))

                    tiempo_transcurrido = time.time() - tiempo_inicial
                    if tiempo_transcurrido > 0:
                        velocidad = progreso.n / (1024 * tiempo_transcurrido)
                        progreso.set_postfix({"Velocidad": f"{velocidad:.2f} kbps",
                                              "Tiempo restante": f"{(tamano_archivo - progreso.n) / (velocidad * 1024):.0f} s"})

                progreso.close()
            print("Archivo descargado con éxito.")
        else:
            print("No se pudo descargar el archivo.")
    except KeyboardInterrupt:
        print("\nDescarga interrumpida por el usuario.")
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except requests.exceptions.HTTPError as e:
        print(f"Error al descargar el archivo: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    while True:
        url, nombre, ubicacion = solicitar_datos_usuario()
        if validar_datos(url, ubicacion):
            descargar_archivo(url, nombre, ubicacion)

        respuesta = input("¿Desea descargar otro archivo? (s/n): ")
        if respuesta.lower() != "s":
            break


if __name__ == "__main__":
    main()