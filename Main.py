import arcade

# ---------------- CONSTANTES ----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "La Oca de Sagaseta - Fichas en Movimiento"

CELL_SIZE = 90
MARGIN = 5

# Colores para los 4 jugadores
PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.YELLOW,
    arcade.color.PURPLE
]

class Ficha:
    def __init__(self, ID, color):
        self.ID = ID
        self.color = color
        self.casilla_actual = 0  # Comienzan fuera del tablero (casilla 0)
        self.radio = 15          # Tamaño de la ficha

class OcaGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        
        self.camino = []
        self.generar_espiral()

        # 1. Creamos los 4 jugadores
        self.jugadores = [Ficha(i, PLAYER_COLORS[i]) for i in range(4)]
        self.turno_actual = 0  # Índice del jugador que le toca mover

    def generar_espiral(self):
        """Calcula las posiciones en espiral (tu lógica original)."""
        total_casillas = 36
        col_inicio, col_fin = 0, 5
        fila_inicio, fila_fin = 0, 5
        n = 1
        
        while n <= total_casillas:
            for i in range(col_inicio, col_fin + 1):
                if n > total_casillas: break
                self.camino.append((i, fila_inicio, n))
                n += 1
            fila_inicio += 1
            for i in range(fila_inicio, fila_fin + 1):
                if n > total_casillas: break
                self.camino.append((col_fin, i, n))
                n += 1
            col_fin -= 1
            for i in range(col_fin, col_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((i, fila_fin, n))
                n += 1
            fila_fin -= 1
            for i in range(fila_fin, fila_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((col_inicio, i, n))
                n += 1
            col_inicio += 1

    def obtener_coordenadas_casilla(self, numero_casilla):
        """Busca los píxeles x, y de una casilla específica."""
        if numero_casilla == 0:
            return 50, 750 # Posición de salida fuera del tablero
        
        offset_x = 125
        offset_y = SCREEN_HEIGHT - 175

        # Buscamos en la lista 'camino' la casilla correspondiente
        for col, fila, num in self.camino:
            if num == numero_casilla:
                x = offset_x + col * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                y = offset_y - fila * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                return x, y
        return 0, 0

    def on_key_press(self, key, modifiers):
        """Se ejecuta cada vez que presionamos una tecla."""
        if key == arcade.key.SPACE:
            # Movemos al jugador actual una casilla
            jugador = self.jugadores[self.turno_actual]
            
            if jugador.casilla_actual < 36:
                jugador.casilla_actual += 1
            
            # Cambiamos el turno al siguiente jugador (0, 1, 2, 3 y vuelve a 0)
            self.turno_actual = (self.turno_actual + 1) % 4

    def on_draw(self):
        self.clear()
        
        offset_x = 125
        offset_y = SCREEN_HEIGHT - 175

        # DIBUJAR TABLERO
        for col, fila, num in self.camino:
            x = offset_x + col * (CELL_SIZE + MARGIN)
            y = offset_y - fila * (CELL_SIZE + MARGIN)

            color_fondo = arcade.color.GREEN
            if num % 5 == 0: color_fondo = arcade.color.GOLD
            if num == 36: color_fondo = arcade.color.INDIAN_RED

            rect = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE)
            arcade.draw_rect_filled(rect, color_fondo)
            arcade.draw_rect_outline(rect, arcade.color.BLACK, 2)
            arcade.draw_text(str(num), x + CELL_SIZE/2, y + CELL_SIZE/2,
                             arcade.color.BLACK, 18, anchor_x="center", anchor_y="center")

        # DIBUJAR FICHAS
        for i, jugador in enumerate(self.jugadores):
            posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual)
            
            # Añadimos un pequeño desplazamiento (offset) para que las fichas 
            # no se tapen totalmente si están en la misma casilla
            desplazamiento = (i - 1.5) * 10 
            
            arcade.draw_circle_filled(posX + desplazamiento, posY + desplazamiento, 
                                      jugador.radio, jugador.color)
            arcade.draw_circle_outline(posX + desplazamiento, posY + desplazamiento, 
                                       jugador.radio, arcade.color.BLACK, 2)

        # Mostrar de quién es el turno
        arcade.draw_text(f"Turno del Jugador: {self.turno_actual + 1}", 
                         400, 750, arcade.color.BLACK, 20, anchor_x="center")

def main():
    game = OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()