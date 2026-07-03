class Thing:
    def __init__(self, id):
        self._id = id

    def get_id(self):
        return self._id

class Persona(Thing):
    def __init__(self, id, nombre):
        super().__init__(id)
        self._nombre = nombre

    def get_nombre(self):
        return self._nombre

class Alumno(Persona):
    def __init__(self, id, nombre, no_control, carrera_sugerida):
        super().__init__(id, nombre)
        self._no_control = no_control
        self._carrera_sugerida = carrera_sugerida

    def get_no_control(self):
        return self._no_control

    def get_carrera_sugerida(self):
        return self._carrera_sugerida

# --- CLASE MODIFICADA ---
class BloqueAptitud(Thing):
    def __init__(self, id, nombre):
        super().__init__(id)
        self._nombre = nombre
        # El puntaje se eliminó de aquí

    def get_nombre(self):
        return self._nombre

# --- NUEVA CLASE INTERMEDIA (Asociación N-aria) ---
class Evaluacion(Thing):
    def __init__(self, id, puntaje):
        super().__init__(id)
        self._puntaje = puntaje

    def get_puntaje(self):
        return self._puntaje

class Carrera(Thing):
    def __init__(self, id, nombre):
        super().__init__(id)
        self._nombre = nombre

    def get_nombre(self):
        return self._nombre