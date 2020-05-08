# mergeGTFS
Comando que permite unir 2 o más GTFS, considerando como estructura base el primer GTFS proporcionado en el directorio (hint: renombre el archivo base como el primero en la lista por orden alfabético).

Los siguientes archivos poseen verificación de coincidencias de id al momento de la unión: 

- agency.txt
- calendar.txt
- calendar_dates.txt
- feed_info.txt
- frequencies.txt
- routes.txt
- shapes.txt
- stop_Times.txt
- stops.txt
- trips.txt

Se omiten aquellos id repetidos conservando el que fue definido en primera instancia (asegurese que los id de los archivos GTFS no sean iguales en caso de representar paraderos, servicios o viajes diferentes).

En caso de incluir archivos fuera de la lista anterior se conservarán en la unión, pero no se verifica la coincidencia de id. 

No hay necesidad de que estén definidos todos los archivos de un GTFS, pero se sugiere que cada uno de ellos sea validado previamente: http://gtfsvalidator.omnimodal.io/upload

## Requisitos

- Python3
- Dependencias (mirar archivo `requirements.txt`)

## Instalación 

Clonar repositorio de Github:

```
git clone https://github.com/Epilef-coder/mergeGTFS.git
```
Cambiar el directorio de trabajo:

```
cd mergeGTFS
```

### Dependencias y entorno virtual (puede omitir este paso si cumple los requisitos)

Se recomienda la utilización de un entorno virtual, si no tiene instalado ```virtualenv``` puede instalarlo con los siguientes comandos:

```pip install virtualenv```, ```pip3 install virtualenv``` o ```pip3 install virtualenv --user```


Luego el entorno virtual puede ser creado dentro de la misma carpeta.

```
virtualenv venv
```

En caso de tener python 2.7 por defecto es necesario definir que sea python3 para el entorno virtual

```
virtualenv -p python3 venv
```


Luego se debe activar el entorno virtual e instalar las dependencias.
 
```
# activar
source venv/bin/activate
 
# instalar dependencias
pip install -r requirements.txt
```

## Ejecución

La ejecución es mediante consola de comando siguiendo la siguiente estructura:

```
python3 mergeGTFS.py \path\to\GTFS
```
## Validación

Si desea validar el GTFS de entrada o salida puede realizarlos a través de: 

- GTFS Meta-Validator (servicio online): http://gtfsvalidator.omnimodal.io/upload
- FeedValidator (en su ordenador): https://github.com/google/transitfeed/wiki/FeedValidator
