import os
import re
import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from urllib.parse import urlparse


def solicitar_datos_usuario():
    # Solicita al usuario la URL, el nombre del archivo y la ubicación de descarga
    url = input("Introduce la URL del archivo: ")
    nombre = input("Introduce el nombre del archivo: ")
    ubicacion = input("Introduce la ubicación donde se guardará el archivo: ")
    return url, nombre, ubicacion


def validar_datos(url, ubicacion):
    # Valida que la URL y la ubicación de descarga sean válidas
    if not validar_url(url):
        print('La URL no es válida.')
        return False

    if not validar_ubicacion(ubicacion):
        print('La ubicación no es válida.')
        return False

    return True


def validar_url(url):
    # Valida que la URL sea válida utilizando el módulo urlparse
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False


def validar_ubicacion(ubicacion):
    # Valida que la ubicación de descarga sea un directorio válido y tenga permisos de escritura
    return os.path.isdir(ubicacion) and os.access(ubicacion, os.W_OK)


def descargar_archivo(url, nombre, ubicacion):
    # Descarga el archivo desde la URL especificada y lo guarda en la ubicación de descarga especificada
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


def descargar_archivo_paralelo(url, nombre, ubicacion, num_hilos):
    # Descarga el archivo desde la URL especificada en paralelo utilizando múltiples hilos
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

                hilos = []
                with ThreadPoolExecutor(max_workers=num_hilos) as executor:
                    for datos in respuesta.iter_content(chunk_size=1024):
                        hilo = executor.submit(archivo.write, datos)
                        hilos.append(hilo)

                    for hilo in tqdm(hilos, total=len(hilos), desc="Descargando", leave=False):
                        hilo.result()

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
    try:
        # Solicita al usuario URL, el nombre del archivo y la ubicación de descarga
        url, nombre, ubicacion = solicitar_datos_usuario()

        # Valida los datos de entrada
        if validar_datos(url, ubicacion):
            # Descarga el archivo utilizando un solo hilo
            descargar_archivo(url, nombre, ubicacion)
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")


if __name__ == "__main__":
    main()
