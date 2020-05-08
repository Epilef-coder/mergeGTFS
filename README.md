# mergeGTFS
Comando que permite unir 2 o más GTFS en uno solo, considerando como estructura base el primer GTFS proporcionado.

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
