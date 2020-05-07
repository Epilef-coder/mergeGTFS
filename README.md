# mergeGTFS
Comando que permite unir 2 o más GTFS en uno solo, considerando como estructura base el primer GTFS proporcionado.

## Requisitos

- Python3
- Dependencias (mirar archivo `requirements.txt`)

## Instalación 

Clonar repositorio de Github:

```
git clone https://github.com/Epilef-coder/GTFS.git
```
Cambiar el directorio de trabajo:

```
cd GTFS
```

### Dependencias y entorno virtual

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
python3 GTFS_frequenciesToScheduled.py \path\to\GTFS_INPUT\GTFS_INPUT.zip
```
#### Prueba

Ejecute test de prueba:

```
python3 GTFS_frequenciesToScheduled.py \path\to\GTFS_INPUT\GTFS_Prueba.zip
```

Si todo sale bien debería tener un retorno como el siguiente:

```
python3 GTFS_frequenciesToScheduled.py \path\to\GTFS_INPUT\GTFS_Prueba.zip
Generando diccionarios
Cambiando frecuencia a itinerario
Generando archivos
Fin, puede encontrar su nuevo GTFS en \path\to\GTFS_INPUT\OUTPUT_SCHEDULED
```
#### Ayuda

```
python3 GTFS_frequenciesToScheduled.py -h

usage: GTFS_frequenciesToScheduled.py [-h] GTFS_INPUT

Cambiar GTFS definido como frecuencia a uno definido por itinerario

positional arguments:
  GTFS_INPUT  Ruta de GTFS INPUT definido como frecuencia. e.g. \path
              o\GTFS_INPUT.zip

optional arguments:
  -h, --help  show this help message and exit
```
