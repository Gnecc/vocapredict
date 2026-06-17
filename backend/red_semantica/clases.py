# Super clase Persona
class Persona():
    def __init__(self, nombre):
        self.nombre = nombre
    
    def setNombre(self, Nnombre):
        if not Nnombre.strip(): 
            print("El campo esta vacio")
        else:
            self.nombre = Nnombre  

    def getNombre(self):
        return self.nombre

# Clase hija Alumno que hereda de Persona
class Alumno(Persona):
    def __init__(self, nombre, no_control, carrera_sugerida):
        super().__init__(nombre)         
        self.no_control = no_control
        self.carrera_sugerida = carrera_sugerida

    def setNoControl(self, Nno_control):
        if not str(Nno_control).strip():
            print("El campo esta vacio")
        else:
            self.no_control = Nno_control  

    def getNoControl(self):
        return self.no_control    

    def setCarreraSugerida(self, Ncarrera_sugerida):
        if not Ncarrera_sugerida.strip():
            print("El campo esta vacio")
        else:
            self.carrera_sugerida = Ncarrera_sugerida 

    def getCarreraSugerida(self):
        return self.carrera_sugerida
     
# Clase Bloque
class Bloque:
    def __init__(self, nombre, puntaje):
        self.nombre = nombre
        self.puntaje = puntaje

    def setNombre(self, Nnombre):
        if not Nnombre.strip():
            print("El campo esta vacio")
        else:
            self.nombre = Nnombre 

    def getNombre(self):
        return self.nombre     

    def setPuntaje(self, Npuntaje):
        if not str(Npuntaje).strip():
            print("El campo esta vacio")
        else:
            self.puntaje = Npuntaje 

    def getPuntaje(self): 
        return self.puntaje  

# Clase Carrera
class Carrera:
    def __init__(self, nombre):
        self.nombre = nombre

    def setNombre(self, Nnombre):
        if not Nnombre.strip():
            print("El campo esta vacio")
        else:
            self.nombre = Nnombre 

    def getNombre(self):
        return self.nombre