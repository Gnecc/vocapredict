"""Roles deterministas para explorar intereses; requieren revisión humana externa."""

from decimal import Decimal

from catalogo import BLOQUES


VERSION_CRITERIO = "intereses-referencia-v1"
MINIMO_INTERES = Decimal("0.70")
MAX_INTERESES = 2


class AgenteIntereses:
    """Selecciona los intereses más altos sin confundir interés con habilidad."""

    def seleccionar(self, puntajes, minimo=MINIMO_INTERES):
        if not puntajes:
            return ()
        ordenados = sorted(((bloque, Decimal(str(valor))) for bloque, valor in puntajes.items()
                            if bloque != "b10"),
                           key=lambda item: (-item[1], item[0]))
        if not ordenados:
            return ()
        corte = ordenados[min(MAX_INTERESES, len(ordenados)) - 1][1]
        return tuple(bloque for bloque, puntaje in ordenados
                     if puntaje >= Decimal(str(minimo)) and puntaje >= corte)


class AgenteVinculos:
    """Expone relaciones provisionales basadas en perfiles de referencia."""

    def relaciones(self):
        return tuple((bloque, carrera)
                     for bloque, _, carreras in BLOQUES
                     for carrera in carreras)


class AgenteRevision:
    """Distingue una pista aislada de varias evidencias concordantes."""

    def nivel(self, numero_evidencias):
        return "convergencia de intereses" if numero_evidencias >= 2 else "pista inicial"
