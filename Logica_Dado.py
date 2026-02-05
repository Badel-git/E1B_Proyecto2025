import random


#Logica
class Dado:
    def tirar(self):
        return random.randint(1, 6)
    


#Uso
dado = Dado()
pasos = dado.tirar()

#Como encajarlo

if key == arcade.key.SPACE:
    jugador = self.jugadores[self.turno_actual]

    pasos = tirar_dado()

    jugador.casilla_actual += pasos
    if jugador.casilla_actual > 36:
        jugador.casilla_actual = 36

    self.turno_actual = (self.turno_actual + 1) % 4
