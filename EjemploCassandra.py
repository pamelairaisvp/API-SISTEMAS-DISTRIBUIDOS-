import threading #Para correr los 3 servidores
from flask import Flask #Para instanciar servidores web
import requests #Realiza solicitudes http get
import os #Control de archivos y directorios
from shutil import rmtree #Eliminación de carpetas enteras

#Instancia de Servidores Web
app0 = Flask(__name__)
app1 = Flask(__name__)
app2 = Flask(__name__)

#Mensaje de redireccionamiento
rv = 'Esta solicitud se realizó por medio de otro servidor. '

#Función hash. define que servidor atenderá la solicitud
def hash_(row):
    if row<0:
        row = -row

    h = row % 3
    return h

#Función que inserta valores a la tabla
def Ins(row, column, cont):
    rp = 'Se guardo el mensaje en la fila '+str(row)+', columna: '+str(column) #Respuesta
    try:
        os.makedirs('Tabla/row'+str(row)) #Crea el directorio que corresponde a la fila
    except OSError as e:
        pass #La fila ya existe
    file=open('Tabla/row'+str(row)+'/column_'+str(column)+'.txt',"w") #Creamos un archivo de texto
    file.write(cont) #Sobreescribimos el contenido de la columna
    file.close() #Cerramos el archivo
    return rp #Devolvemos respuesta

#Lee el contedido de una columna
def Get(row, column):
    try:
        file=open('Tabla/row'+str(row)+'/column_'+str(column)+'.txt',"r") #Abre el archivo
        rd = str(file.read()) #Guarda la cadena como respuesta
        file.close() #Cierra el archivo
    except:
        rd = "La localidad solicidada no existe en la tabla" #No se ha creado la fila/columna
    return rd

#Elimina el contenido de una columna
def DeleteC(row, column):
    try:
        os.remove('Tabla/row'+str(row)+'/column_'+str(column)+'.txt')
        rd = "Se eliminó el contenido"
    except:
        rd = "La localidad solicidada no existe en la tabla"
    return rd

#Elimina una fila completa, junto con todas sus columnas y su contenido
def DeleteR(row):
    try:
        rmtree('Tabla/row'+str(row))
        rd = "Se eliminó la fila "+str(row)
    except:
        rd = "La fila solicidada no existe en la tabla"
    return rd

#Corre el Servidor0
def Servidor0():
    app0.run(port=5000)

#Función que se ejecuta cuando la url es la siguiente:
@app0.route("/insert/<row>/<column>/<cont>")
def insert0(row, column, cont):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==0: #Verifica que le corresponde atender la solicitud
        if row==0: #fila invalida
            return 'La fila cero no puede ser utilizada en la base,\npor favor inicie la tabla en row = 1'
        else:
            if row<0: #Fila negativa indica que la solicitud proviene de otro servidor
                row = -row #Corrige fila negativa
                rp  = Ins(row,column,cont) #Insertamos contenido
                sr = 'El servidor (0) atendió esta solicitud. '
                return rv+sr+rp
            else: #La solicitud no ha sido redireccionada desde ningún servidor
                sr = 'Este servidor (0) atiende la solicitud. '
                rp  = Ins(row,column,cont)
                return sr+rp

    else: #No le corresponde atender esta solicitud, reenvia al servidor correcto
        url = "http://localhost:500"+str(h)+"/insert/"+str(-row)+"/"+str(column)+"/"+cont
                                        #Fila negativa indica reenvío (-row)
        r = requests.get(url)
        response = r.text
        return response #Respuesta del otro servidor

#Función del Serv0 para leer localidades de la tabla
@app0.route("/get/<row>/<column>")
def get0(row, column):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==0:
        if row==0: #Fila cero inhabilitada
            return 'La fila cero no puede ser utilizada en la base,\npor favor inicie la tabla en row = 1'
        else:
            if row<0: #Fila negativa. reenvío
                row = -row #Corrección de fila negativa
                rp  = Get(row,column) #Lee contenido
                sr = 'El servidor (0) atendió esta solicitud. '
                return rv+sr+'contenido: '+rp #Responde
            else:
                sr = 'Este servidor (0) atiende la solicitud. ' #Servidor nativo
                rp  = Get(row,column) #Lee contenido
                return sr+'Contenido: '+rp #Responde

    else: #No le corresponde atender esta solicitud, reenvia al servidor correcto
        url = "http://localhost:500"+str(h)+"/get/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response

#Función que borra CONTENIDO. serv0
@app0.route("/delete/<row>/<column>")
def deleteC0(row, column):
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==0:
        if row==0: #Fila cero inhabilitada
            return 'La fila cero no puede ser utilizada en la base,\npor favor inicie la tabla en row = 1'
        else:
            if row<0: #Fila negativa. reenvío
                row = -row #Corrección fila negativa
                rp  = DeleteC(row,column) #Borra contenido
                sr = 'El servidor (0) atendió esta solicitud. '
                return rv+sr+rp #Responde
            else:
                sr = 'Este servidor (0) atiende la solicitud. '
                rp  = DeleteC(row,column) #Borra contenido
                return sr+rp #Responde

    else: #No le corresponde atender esta solicitud, reenvia al servidor correcto
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response

#Función que borra FILAS. serv0
@app0.route("/delete/<row>")
def deleteR0(row):
    h = hash_(int(row))
    row = int(row)
    if h==0: #Verifica que le toque atender la solicitud
        if row==0: #fila cero inhabilitada
            return 'La fila cero no puede ser utilizada en la base,\npor favor inicie la tabla en row = 1'
        else:
            if row<0: #Fila negativa. reenvío
                row = -row #Corrección de fila negativa
                rp  = DeleteR(row) #Elimina fila
                sr = 'El servidor (0) atendió esta solicitud. '
                return rv+sr+rp
            else:
                sr = 'Este servidor (0) atiende la solicitud. '
                rp  = DeleteR(row)
                return sr+rp

    else: #No le corresponde atender esta solicitud, reenvia al servidor correcto
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)
        r = requests.get(url)
        response = r.text
        return response
###########################################################
    
def Servidor1():
    app1.run(port=5001)
    
@app1.route("/insert/<row>/<column>/<cont>")
def insert1(row, column, cont):
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==1:
        if row<0:
            row = -row
            rp  = Ins(row,column,cont)
            sr = 'El servidor (1) atendió esta solicitud'
            return rv+sr+rp
        else:
            sr = 'Este servidor (1) atiende la solicitud'
            rp  = Ins(row,column,cont)
            return sr+rp
    else:
        url = "http://localhost:500"+str(h)+"/insert/"+str(-row)+"/"+str(column)+"/"+cont
        r = requests.get(url)
        response = r.text
        return response

@app1.route("/get/<row>/<column>")
def get1(row, column):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==1:
        if row<0:
            row = -row
            rp  = Get(row,column)
            sr = 'El servidor (1) atendió esta solicitud. '
            return rv+sr+'contenido: '+rp
        else:
            sr = 'Este servidor (1) atiende la solicitud. '
            rp  = Get(row,column)
            return sr+'Contenido: '+rp

    else:
        url = "http://localhost:500"+str(h)+"/get/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response

@app1.route("/delete/<row>/<column>")
def deleteC1(row, column):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==1:
        if row<0:
            row = -row
            rp  = DeleteC(row,column)
            sr = 'El servidor (1) atendió esta solicitud. '
            return rv+sr+rp
        else:
            sr = 'Este servidor (1) atiende la solicitud. '
            rp  = DeleteC(row,column)
            return sr+rp

    else:
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response
    
@app1.route("/delete/<row>")
def deleteR1(row):
    global rv
    h = hash_(int(row))
    row = int(row)
    if h==1:
        if row<0:
            row = -row
            rp  = DeleteR(row)
            sr = 'El servidor (1) atendió esta solicitud. '
            return rv+sr+rp
        else:
            sr = 'Este servidor (1) atiende la solicitud. '
            rp  = DeleteR(row)
            return sr+rp

    else:
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)
        r = requests.get(url)
        response = r.text
        return response

####################################################################

def Servidor2():
    app2.run(port=5002)
    
@app2.route("/insert/<row>/<column>/<cont>")
def insert2(row, column, cont):
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==2:
        if row<0:
            row = -row
            rp  = Ins(row,column,cont)
            sr = 'El servidor (2) atendió esta solicitud'
            return rv+sr+rp
        else:
            sr = 'Este servidor (2) atiende la solicitud'
            rp  = Ins(row,column,cont)
            return sr+rp
    else:
        url = "http://localhost:500"+str(h)+"/insert/"+str(-row)+"/"+str(column)+"/"+cont
        r = requests.get(url)
        response = r.text
        return response

@app2.route("/get/<row>/<column>")
def get2(row, column):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==2:
        if row<0:
            row = -row
            rp  = Get(row,column)
            sr = 'El servidor (2) atendió esta solicitud. '
            return rv+sr+'Contenido: '+rp
        else:
            sr = 'Este servidor (2) atiende la solicitud. '
            rp  = Get(row,column)
            return sr+'contenido: '+rp

    else:
        url = "http://localhost:500"+str(h)+"/get/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response


@app2.route("/delete/<row>/<column>")
def deleteC2(row, column):
    global rv
    h = hash_(int(row))
    row = int(row)
    column = int(column)
    if h==2:
        if row<0:
            row = -row
            rp  = DeleteC(row,column)
            sr = 'El servidor (2) atendió esta solicitud. '
            return rv+sr+rp
        else:
            sr = 'Este servidor (2) atiende la solicitud. '
            rp  = DeleteC(row,column)
            return sr++rp

    else:
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)+"/"+str(column)
        r = requests.get(url)
        response = r.text
        return response

@app2.route("/delete/<row>")
def deleteR2(row):
    global rv
    h = hash_(int(row))
    row = int(row)
    if h==2:
        if row<0:
            row = -row
            rp  = DeleteR(row)
            sr = 'El servidor (2) atendió esta solicitud. '
            return rv+sr+rp
        else:
            sr = 'Este servidor (2) atiende la solicitud. '
            rp  = DeleteR(row)
            return sr+rp

    else:
        url = "http://localhost:500"+str(h)+"/delete/"+str(-row)
        r = requests.get(url)
        response = r.text
        return response

#Se instancian los hilos
s0 = threading.Thread(name="Servidor0", target=Servidor0)
s1 = threading.Thread(name="Servidor1", target=Servidor1)
s2 = threading.Thread(name="Servidor2", target=Servidor2)

#Se ejecutan los hilos
s0.start()
s1.start()
s2.start()