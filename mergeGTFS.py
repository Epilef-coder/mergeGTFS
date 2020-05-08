# compatibilidad de columnas
from collections import defaultdict
import pandas as pd
import zipfile
import shutil
import collections
import numpy as np

import argparse
import os
import sys
import errno

from os import listdir
from os.path import isfile
from os import remove

# add path so we can use function through command line
new_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(new_path)


# lista de archivos de una ruta
def listaarchivos(path):
    return [obj for obj in listdir(path) if isfile(path + obj)]


# verifica si un archivo es zip
def zip(arch):
    return arch.endswith('.zip')


# verifica si un archivo es txt
def txt(arch):
    return arch.endswith('.txt')


# generamos archivo txt con formato similar a uno de base
def copiarformato(base, nuevo):
    # stop_times
    d = defaultdict(list)
    for i in base.columns:
        # print(i)
        d[i] = nuevo[i]
    final = pd.DataFrame()
    for i in base.columns:
        final[i] = d[i]

    return final


def main(argv):
    # archivos GTFS que se identifican coincidencias de ID
    procesados = ["agency.txt", "calendar.txt", "calendar_dates.txt", "feed_info.txt", "frequencies.txt", "routes.txt",
                  "shapes.txt", "stop_times.txt", "stops.txt", "trips.txt"]

    # Arguments and description
    parser = argparse.ArgumentParser(
        description='Unir dos o más GTFS (GTFS.zip), manteniendo la compatibilidad con el primer GTFS (GTFS base).')
    parser.add_argument('GTFS_path', action="store",
                        help='Ruta donde GTFS están almacenados, el primero de ellos será tomado como referencia. '
                             'e.g. \path\to\GTFS_INPUT')

    args = parser.parse_args(argv[1:])

    # Give names to arguments
    route = args.GTFS_path
    route_output = route + '\\OUTPUT_MERGE'

    # intentamos crear directorio de salida si no existe
    try:
        os.mkdir(route_output)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Creamos listas de archivos (.zip)
    archivos = listaarchivos(route + "\\")
    archivoszip = []
    for a in archivos:
        if zip(a):
            archivoszip.append(a)

    print("")
    print("Archivos GTFS que se procesaran: {}".format(archivoszip))

    n = 0
    gtfsbase = ""
    for gtfs in archivoszip:
        if n == 0:
            gtfsbase = gtfs
            print("")
            print("GTFS base: {}".format(gtfsbase))

            # tomamos GTFS base y lo copiamos en ruta destino
            fuente = route + "\\" + gtfs
            destino = route_output + "\\GTFS_MERGE.zip"
            shutil.copyfile(fuente, destino)
            n = n + 1
        else:
            # extraemos archivos de gtfs base
            z = zipfile.ZipFile(route_output + "\\GTFS_MERGE.zip")
            z.extractall(route_output)
            z.close()

            # extraemos archivos de gtfs 2
            z = zipfile.ZipFile(route + "\\" + gtfs)
            z.extractall(route)
            z.close()

            n = n + 1

            # verificamos aquellos archivos que existen exclusivamente en un solo GTFS y estos se copian sin procesar

            # datos gtfs base
            archivosbase = listaarchivos(route_output + "\\")
            archivosbasetxt = []
            for a in archivosbase:
                if txt(a):
                    archivosbasetxt.append(a)

            # datos gtfs 2
            archivos2 = listaarchivos(route + "\\")
            archivos2txt = []
            for a in archivos2:
                if txt(a):
                    archivos2txt.append(a)

            # identificamos archivos en ambos GTFS y aquellos que solo estan en uno
            norepetidosbase = []
            norepetidos2 = []
            repetidos = []

            for item in archivosbasetxt:
                if item in archivos2txt:
                    repetidos.append(item)
                else:
                    norepetidosbase.append(item)

            for item in archivos2txt:
                if item not in archivosbasetxt:
                    norepetidos2.append(item)

            print("")
            print("Union de GTFS base \'{}\' con GTFS nuevo \'{}\'".format(gtfsbase, gtfs))
            print("Archivos repetidos            : {}".format(repetidos))
            print("Archivos no repetidos en base : {}".format(norepetidosbase))
            print("Archivos no repetidos en nuevo: {}".format(norepetidos2))

            # aquellos archivos no repetidos son copiados tal cual (identificados)
            # aquellos archivos repetidos se conserva la estructura de columnas del archivo base
            # aquellos archivos repetidos que no sean parte de los archivos:
            # agency.txt, calendar.txt, calendar_dates.txt, feed_info.txt, frequencies.txt
            # routes.txt,  shapes.txt, stop_times.txt, stops.txt,  trips.txt
            # se copian filas sin verificar coincidencias de id

            # no repetidos en base se mantienen

            # no repetidos en nuevo se copia
            for file in norepetidos2:
                fuente = route + "\\" + file
                destino = route_output + "\\" + file
                shutil.copyfile(fuente, destino)

            # dos archivos repetidos, se le copian las filas solamente respetando formato de archivo base
            for file in repetidos:
                # se copian directamente las filas
                if file not in procesados:
                    filebase = pd.read_csv(route_output + "\\" + file, sep=",")
                    filenuevo = pd.read_csv(route + "\\" + file, sep=",")

                    # filenuevo con formato igual al base
                    filenuevo = copiarformato(filebase, filenuevo)

                    # unimos filas de filebase y file nuevo
                    filefinal = pd.concat([filebase, filenuevo], axis=0)

                    filefinal.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                # corresponde a los archivos que hay que realizar una verificacion de id
                else:
                    if file == "agency.txt":

                        print("")
                        print("INICIO {}".format(file))
                        agency = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_agency = pd.read_csv(route + "\\" + file, sep=",")
                        # no se aguanta un mismo agency_id

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base y nuevo
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in agency.columns:
                            # inicializamos diccionarios
                            d1[i] = agency[i]
                            d2[i] = new_agency[i]

                            # si hay id repetidos no se agregan
                            if i == 'agency_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["agency_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["agency_id"][i]):
                                for columnas in agency.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo agency base     : {} filas".format(len(d1['agency_id'])))
                        print("Largo agency 2        : {} filas".format(len(d2['agency_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("Agencias agregadas    : {}".format(cs))
                        print("Agencias no agregadas : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in agency.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_agency = pd.concat([agency, agregar])
                        # escritura de dataframe
                        end_agency.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        banagency = no_agregados

                        print("Largo agency final    : {} filas".format(len(end_agency)))
                        print("")
                        print("Fin agency")
                        continue

                    if file == "calendar.txt":
                        # calendar
                        # no se aguanta repeticion de service_id
                        print("")
                        print("INICIO {}".format(file))

                        calendar = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_calendar = pd.read_csv(route + "\\" + file, sep=",")

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in calendar.columns:
                            # inicializamos diccionarios
                            d1[i] = calendar[i]
                            d2[i] = new_calendar[i]

                            # si hay id repetidos no se agregan
                            if i == 'service_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["service_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["service_id"][i]):
                                for columnas in calendar.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo calendar base     : {} filas".format(len(d1['service_id'])))
                        print("Largo calendar 2        : {} filas".format(len(d2['service_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("servicios  agregadas    : {}".format(cs))
                        print("servicios  no agregadas : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in calendar.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_calendar = pd.concat([calendar, agregar])
                        # escritura de dataframe
                        end_calendar.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')
                        bancalendar = no_agregados

                        print("Largo calendar final    : {} filas".format(len(end_calendar)))
                        print("")

                        print("Fin calendar")
                        continue

                    if file == "calendar_dates.txt":
                        print("")
                        print("INICIO {}".format(file))

                        calendar_dates = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_calendar_dates = pd.read_csv(route + "\\" + file, sep=",")

                        # no se aguanta service_id repetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in calendar_dates.columns:
                            # inicializamos diccionarios
                            d1[i] = calendar_dates[i]
                            d2[i] = new_calendar_dates[i]

                            # si hay id repetidos no se agregan
                            if i == 'service_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["service_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["service_id"][i]):
                                for columnas in calendar_dates.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo calendar_dates base     : {} filas".format(len(d1['service_id'])))
                        print("Largo calendar_dates 2        : {} filas".format(len(d2['service_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("calendar_dates  agregadas     : {}".format(cs))
                        print("calendar_dates  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in calendar_dates.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_calendar_dates = pd.concat([calendar_dates, agregar])
                        # escritura de dataframe
                        end_calendar_dates.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        bancalendar_dates = no_agregados

                        print("Largo calendar_dates final    : {} filas".format(len(end_calendar_dates)))
                        print("")
                        print("Fin calendar_dates")

                        continue

                    if file == "feed_info.txt":

                        print("")
                        print("INICIO {}".format(file))

                        feed_info = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_feed_info = pd.read_csv(route + "\\" + file, sep=",")

                        # no se aguanta feed_publisher_name repetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in feed_info.columns:
                            # inicializamos diccionarios
                            d1[i] = feed_info[i]
                            d2[i] = new_feed_info[i]

                            # si hay id repetidos no se agregan
                            if i == 'feed_publisher_name':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["feed_publisher_name"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["feed_publisher_name"][i]):
                                for columnas in feed_info.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo feed_info base     : {} filas".format(len(d1['feed_publisher_name'])))
                        print("Largo feed_info 2        : {} filas".format(len(d2['feed_publisher_name'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("feed_info  agregadas     : {}".format(cs))
                        print("feed_info  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in feed_info.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_feed_info = pd.concat([feed_info, agregar])
                        # escritura de dataframe
                        end_feed_info.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        banfeed_info = no_agregados

                        print("Largo feed_info final    : {} filas".format(len(end_feed_info)))
                        print("")
                        print("Fin feed_info")

                        continue
                    if file == "frequencies.txt":

                        print("")
                        print("INICIO {}".format(file))

                        frequencies = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_frequencies = pd.read_csv(route + "\\" + file, sep=",")

                        # no se aguanta trip_id repetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in frequencies.columns:
                            # inicializamos diccionarios
                            d1[i] = frequencies[i]
                            d2[i] = new_frequencies[i]

                            # si hay id repetidos no se agregan
                            if i == 'trip_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["trip_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["trip_id"][i]):
                                for columnas in frequencies.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo frequencies base     : {} filas".format(len(d1['trip_id'])))
                        print("Largo frequencies 2        : {} filas".format(len(d2['trip_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("frequencies  agregadas     : {}".format(cs))
                        print("frequencies  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in frequencies.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_frequencies = pd.concat([frequencies, agregar])
                        # escritura de dataframe
                        end_frequencies.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        banfrequencies = no_agregados
                        # para mandar a stop_times
                        # nobanfrequencies = agregados

                        print("Largo frequencies final    : {} filas".format(len(end_frequencies)))
                        print("")
                        print("Fin frequencies")

                        continue

                    if file == "routes.txt":

                        print("")
                        print("INICIO {}".format(file))

                        routes = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_routes = pd.read_csv(route + "\\" + file, sep=",")

                        # routes
                        # no se aguanta route_id y route_short_namerepetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        agregados_2 = defaultdict(list)
                        no_agregados_2 = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        s2 = []
                        n2 = []

                        for i in routes.columns:
                            # inicializamos diccionarios
                            d1[i] = routes[i]
                            d2[i] = new_routes[i]

                            # si hay id repetidos no se agregan
                            if i == 'route_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if (j == k):
                                            jagregar = False
                                    if (jagregar):
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                            # si hay id repetidos no se agregan
                            if i == 'route_short_name':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados_2[j].append(1)
                                        s2.append(j)
                                    else:
                                        no_agregados_2[j].append(1)
                                        n2.append(j)
                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["route_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["route_id"][i]) and agregados_2.get(d2["route_short_name"][i]):
                                for columnas in routes.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo routes base       : {} filas".format(len(d1['route_id'])))
                        print("Largo routes 2          : {} filas".format(len(d2['route_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("routes  agregadas       : {}".format(cs))
                        print("routes  no agregadas    : {}".format(cn))
                        print("")

                        cs2 = collections.Counter(s2)
                        cn2 = collections.Counter(n2)

                        print("routes  agregadas_2     : {}".format(cs2))
                        print("routes  no agregadas_2  : {}".format(cn2))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in routes.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_routes = pd.concat([routes, agregar])
                        # escritura de dataframe
                        end_routes.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        banroutes = no_agregados
                        banroutes_2 = no_agregados_2

                        print("Largo routes final      : {} filas".format(len(end_routes)))
                        print("")
                        print("Fin routes")

                        continue
                    if file == "shapes.txt":

                        print("")
                        print("INICIO {}".format(file))

                        shapes = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_shapes = pd.read_csv(route + "\\" + file, sep=",")
                        # no se aguanta shape_id

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in shapes.columns:
                            # inicializamos diccionarios
                            d1[i] = shapes[i]
                            d2[i] = new_shapes[i]

                            # si hay id repetidos no se agregan
                            if i == 'shape_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if (j == k):
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["shape_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["shape_id"][i]):
                                for columnas in shapes.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo shapes base     : {} filas".format(len(d1['shape_id'])))
                        print("Largo shapes 2        : {} filas".format(len(d2['shape_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("routes  agregadas     : {}".format(cs))
                        print("routes  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in shapes.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_shapes = pd.concat([shapes, agregar])
                        # escritura de dataframe
                        end_shapes.to_csv(route_output + "\\" + file , header=True, index=False, sep=',')

                        banshapes = no_agregados

                        print("Largo shapes final    : {} filas".format(len(end_shapes)))
                        print("")
                        print("Fin shapes")

                        continue
                    if file == "stop_times.txt":

                        print("")
                        print("INICIO {}".format(file))

                        stop_times = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_stop_times = pd.read_csv(route + "\\" + file, sep=",")

                        # no se aguanta trip_id repetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in stop_times.columns:
                            # inicializamos diccionarios
                            d1[i] = stop_times[i]
                            d2[i] = new_stop_times[i]

                            # si hay id repetidos no se agregan
                            if i == 'trip_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["trip_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["trip_id"][i]):
                                for columnas in stop_times.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo stop_times base     : {} filas".format(len(d1['trip_id'])))
                        print("Largo stop_times 2        : {} filas".format(len(d2['trip_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("stop_times  agregadas     : {}".format(cs))
                        print("stop_times  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in stop_times.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_stop_times = pd.concat([stop_times, agregar])
                        # escritura de dataframe
                        end_stop_times.to_csv(route_output + "\\"+ file, header=True, index=False, sep=',')

                        banstoptimes = no_agregados

                        print("Largo stop_times final    : {} filas".format(len(end_stop_times)))
                        print("")
                        print("Fin stop_times")

                        continue
                    if file == "stops.txt":

                        print("")
                        print("INICIO {}".format(file))

                        stops = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_stops = pd.read_csv(route + "\\" + file, sep=",")

                        # stops
                        # no se aguanta stop_id repetido

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in stops.columns:
                            # inicializamos diccionarios
                            d1[i] = stops[i]
                            d2[i] = new_stops[i]

                            # si hay id repetidos no se agregan
                            if i == 'stop_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["stop_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["stop_id"][i]):
                                for columnas in stops.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo stops base     : {} filas".format(len(d1['stop_id'])))
                        print("Largo stops 2        : {} filas".format(len(d2['stop_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("stops  agregadas     : {}".format(cs))
                        print("stops  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in stops.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_stops = pd.concat([stops, agregar])
                        # escritura de dataframe
                        end_stops.to_csv(route_output + "\\" + file, header=True, index=False, sep=',')

                        banstops = no_agregados

                        print("Largo stops final    : {} filas".format(len(end_stops)))
                        print("")
                        print("Fin stops")

                        continue
                    if file == "trips.txt":

                        print("")
                        print("INICIO {}".format(file))

                        trips = pd.read_csv(route_output + "\\" + file, sep=",")
                        new_trips = pd.read_csv(route + "\\" + file, sep=",")

                        # id que se agregan y no porque estan repetidos
                        agregados = defaultdict(list)
                        no_agregados = defaultdict(list)

                        # diccionarios con datos base (d1) y nuevo (d2)
                        d1 = defaultdict(list)
                        d2 = defaultdict(list)

                        # arreglo con los aceptados y rechazados
                        s = []
                        n = []

                        for i in trips.columns:
                            # inicializamos diccionarios
                            d1[i] = trips[i]
                            d2[i] = new_trips[i]

                            # si hay id repetidos no se agregan
                            if i == 'trip_id':
                                for j in d2[i]:
                                    jagregar = True
                                    for k in d1[i]:
                                        if j == k:
                                            jagregar = False
                                    if jagregar:
                                        agregados[j].append(1)
                                        s.append(j)
                                    else:
                                        no_agregados[j].append(1)
                                        n.append(j)

                        # diccionario solo con datos que se agregaran
                        dagregar = defaultdict(list)
                        # recorremos d2 y verificamos si se agrega fila o no
                        for i in range(len(d2["trip_id"])):
                            # print(i)
                            # esta en la lista de agregados
                            if agregados.get(d2["trip_id"][i]):
                                for columnas in trips.columns:
                                    dagregar[columnas].append(d2[columnas][i])

                        print("Largo trips base     : {} filas".format(len(d1['trip_id'])))
                        print("Largo trips 2        : {} filas".format(len(d2['trip_id'])))
                        print("")

                        cs = collections.Counter(s)
                        cn = collections.Counter(n)

                        print("trips  agregadas     : {}".format(cs))
                        print("trips  no agregadas  : {}".format(cn))
                        print("")

                        # dataframe solo con datos que se agregan
                        agregar = pd.DataFrame()
                        for i in trips.columns:
                            agregar[i] = dagregar[i]

                        # dataframe final
                        end_trips = pd.concat([trips, agregar])
                        # escritura de dataframe
                        end_trips.to_csv(route_output + "\\" + file , header=True, index=False, sep=',')

                        bantrips = no_agregados

                        print("Largo trips final    : {} filas".format(len(end_trips)))
                        print("")
                        print("Fin trips")

                        continue

            #compilamos archivos en route_output y eliminamos txt

            # comprimimos archivos OUTPUT en zip
            ze = zipfile.ZipFile(route_output + "\\GTFS_MERGE.zip", 'w')
            for folder, subfolders, files in os.walk(route_output):
                for file in files:
                    if file.endswith('.txt'):
                        ze.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder, file), route_output),
                                 compress_type=zipfile.ZIP_DEFLATED)
            ze.close()

            # datos gtfs base
            archivosbase = listaarchivos(route_output + "\\")
            for a in archivosbase:
                if txt(a):
                    remove(route_output + "\\" + a)

            # datos gtfs 2
            archivos2 = listaarchivos(route + "\\")
            for a in archivos2:
                if txt(a):
                    remove(route + "\\" + a)


if __name__ == "__main__":
    # print(sys.argv)
    sys.exit(main(sys.argv))