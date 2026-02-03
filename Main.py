import arcade

# ---------------- CONSTANTES ----------------
# Definimos el tamaño de la ventana y de las casillas. 
# Usar constantes permite cambiar el diseño rápidamente sin tocar la lógica.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "La Oca de Sagaseta - Espiral Clásica"

CELL_SIZE = 90  # Tamaño en píxeles de cada lado de la casilla
MARGIN = 5     # Espacio de separación entre casillas

class OcaGame(arcade.Window):
    def __init__(self):
        # Inicializamos la ventana con las constantes de arriba
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # Color de fondo de la ventana (el lienzo sobre el que dibujamos)
        arcade.set_background_color(arcade.color.WHITE)
        
        # Lista vacía donde guardaremos las coordenadas (x, y) y el número de cada casilla
        self.camino = []
        # Llamamos a la función que calcula las posiciones
        self.generar_espiral()

    def generar_espiral(self):
        """Lógica para calcular las posiciones en forma de espiral hacia adentro."""
        total_casillas = 36 # Tablero de 6x6
        
        # Estos índices controlan los límites de la espiral que se van cerrando
        col_inicio, col_fin = 0, 5
        fila_inicio, fila_fin = 0, 5
        
        n = 1 # Contador para el número de la casilla (del 1 al 36)
        
        # El bucle continúa hasta que hayamos calculado las 36 posiciones
        while n <= total_casillas:
            
            # 1. MOVIENDO A LA DERECHA (Fila superior)
            # Recorre las columnas de la fila superior actual
            for i in range(col_inicio, col_fin + 1):
                if n > total_casillas: break
                self.camino.append((i, fila_inicio, n))
                n += 1
            # Como ya llenamos la fila de arriba, el siguiente límite superior baja una fila
            fila_inicio += 1

            # 2. MOVIENDO HACIA ABAJO (Columna derecha)
            # Recorre las filas de la columna derecha actual
            for i in range(fila_inicio, fila_fin + 1):
                if n > total_casillas: break
                self.camino.append((col_fin, i, n))
                n += 1
            # El límite derecho se mueve una columna a la izquierda
            col_fin -= 1

            # 3. MOVIENDO A LA IZQUIERDA (Fila inferior)
            # Recorre hacia atrás las columnas de la fila inferior actual
            for i in range(col_fin, col_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((i, fila_fin, n))
                n += 1
            # El límite inferior sube una fila
            fila_fin -= 1

            # 4. MOVIENDO HACIA ARRIBA (Columna izquierda)
            # Recorre hacia arriba las filas de la columna izquierda actual
            for i in range(fila_fin, fila_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((col_inicio, i, n))
                n += 1
            # El límite izquierdo se mueve una columna a la derecha
            col_inicio += 1
            # Al terminar este paso, el cuadro es más pequeño y el ciclo se repite hacia adentro

    def on_draw(self):
        """Esta función se encarga de renderizar todo en pantalla."""
        self.clear() # Limpia la pantalla en cada fotograma
        
        # Puntos de referencia para que el tablero no esté pegado a los bordes
        offset_x = 125
        offset_y = SCREEN_HEIGHT - 175

        # Recorremos la lista de posiciones que generamos en 'generar_espiral'
        for col, fila, num in self.camino:
            # Convertimos los índices (0,1,2...) en píxeles reales multiplicando por el tamaño
            x = offset_x + col * (CELL_SIZE + MARGIN)
            y = offset_y - fila * (CELL_SIZE + MARGIN)

            # Lógica de colores según el número de casilla
            color_fondo = arcade.color.GREEN
            if num % 5 == 0: 
                color_fondo = arcade.color.GOLD # Casillas especiales "de oca a oca"
            if num == 36: 
                color_fondo = arcade.color.INDIAN_RED # Casilla de meta

            # Creamos el rectángulo con las coordenadas calculadas
            rect = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE)
            
            # Dibujamos el relleno y el borde negro
            arcade.draw_rect_filled(rect, color_fondo)
            arcade.draw_rect_outline(rect, arcade.color.BLACK, 2)

            # Dibujamos el número en el centro de la casilla
            arcade.draw_text(
                str(num),
                x + CELL_SIZE/2, y + CELL_SIZE/2,
                arcade.color.BLACK, 18,
                anchor_x="center", anchor_y="center", bold=True
            )

def main():
    # Crea una instancia de la clase OcaGame y arranca el motor del juego
    OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()
