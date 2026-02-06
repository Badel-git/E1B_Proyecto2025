import arcade
import os
import urllib.request
import random

# --- 1. CONFIGURACIÓN ---
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

# --- 2. CONSTANTES ---
SCREEN_TITLE = "La Oca - Versión Master (F11 para Pantalla Completa)"

# URL DEL FONDO (Pizarra)
URL_FONDO = "https://i.postimg.cc/Qx0fKVpd/Fondo-Tablero.jpg"

# URL DE LA CASILLA 1 (Bandera)
URL_CASILLA_1 = "https://i.postimg.cc/Sxh5FjWh/bandera.png"

CELL_SIZE = 120
MARGIN = 5

PLAYER_COLORS = [
    arcade.color.RED,
    arcade.color.BLUE,
    arcade.color.YELLOW,
    arcade.color.PURPLE
]


class Dado:
    def tirar(self):
        return random.randint(1,6)
    
#Uso 
dado = Dado()
pasos = dado.tirar()

class Ficha:
    def __init__(self, ID, color):
        self.ID = ID
        self.color = color
        self.casilla_actual = 0
        self.radio = 25

class OcaGame(arcade.Window):
    def __init__(self):
        # Arrancamos en pantalla completa
        super().__init__(title=SCREEN_TITLE, fullscreen=True)
        
        # Variables para texturas
        self.background = None
        self.usar_imagen_fondo = False
        self.textura_casilla_1 = None 

        # --- MENSAJE DE CARGA ---
        print("Cargando recursos... ⚙️")

        # --- CARGA NINJA ---
        self.cargar_textura_ninja(URL_FONDO, "temp_fondo.jpg", es_fondo=True)
        self.cargar_textura_ninja(URL_CASILLA_1, "temp_c1.png", es_fondo=False)

        self.camino = []
        self.generar_espiral()
        self.jugadores = [Ficha(i, PLAYER_COLORS[i]) for i in range(4)]
        self.turno_actual = 0

    def cargar_textura_ninja(self, url, nombre_temp, es_fondo):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(nombre_temp, 'wb') as out_file:
                out_file.write(response.read())
            
            textura = arcade.load_texture(nombre_temp)
            
            if es_fondo:
                self.background = textura
                self.usar_imagen_fondo = True
            else:
                self.textura_casilla_1 = textura

            if os.path.exists(nombre_temp):
                os.remove(nombre_temp)
                
        except Exception:
            # Si falla, silencio (o fondo gris)
            if es_fondo: self.background_color = arcade.color.GRAY

    def generar_espiral(self):
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

    def obtener_offsets(self):
        # Se adapta al tamaño actual de la ventana
        tablero_ancho = 6 * (CELL_SIZE + MARGIN)
        tablero_alto = 6 * (CELL_SIZE + MARGIN)
        
        off_x = (self.width - tablero_ancho) // 2
        ajuste_bajar = 110
        off_y = (self.height // 2) + (tablero_alto // 2) - CELL_SIZE - ajuste_bajar
        return off_x, off_y

    def obtener_coordenadas_casilla(self, numero_casilla):
        if numero_casilla == 0:
            off_x, _ = self.obtener_offsets()
            return off_x - 100, self.height // 2 

        off_x, off_y = self.obtener_offsets()

        for col, fila, num in self.camino:
            if num == numero_casilla:
                x = off_x + col * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                y = off_y - fila * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                return x, y
        return 0, 0

    def on_key_press(self, key, modifiers):
        # --- ESC: SALIR ---
        if key == arcade.key.ESCAPE:
            self.close()
            
        # --- F11: PANTALLA COMPLETA / VENTANA ---
        elif key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            if not self.fullscreen:
                self.set_size(1280, 720)
                self.center_window()

        # --- ESPACIO: MOVER ---    
        elif key == arcade.key.SPACE:
            jugador = self.jugadores[self.turno_actual]
            pasos = dado.tirar()

            if jugador.casilla_actual < 36:
                jugador.casilla_actual += pasos
            self.turno_actual = (self.turno_actual + 1) % 4

    def on_draw(self):
        self.clear()

        # 1. FONDO
        if self.usar_imagen_fondo and self.background:
            rect_fondo = arcade.XYWH(self.width / 2, self.height / 2, self.width, self.height)
            arcade.draw_texture_rect(self.background, rect_fondo)

        off_x, off_y = self.obtener_offsets()

        # 2. TABLERO
        for col, fila, num in self.camino:
            x = off_x + col * (CELL_SIZE + MARGIN)
            y = off_y - fila * (CELL_SIZE + MARGIN)
            
            rect_casilla = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE)

            # Casilla 1 Bandera
            if num == 1 and self.textura_casilla_1:
                arcade.draw_texture_rect(self.textura_casilla_1, rect_casilla)
            else:
                color_fondo = arcade.color.GREEN
                if num % 5 == 0: color_fondo = arcade.color.GOLD
                if num == 36: color_fondo = arcade.color.INDIAN_RED
                arcade.draw_rect_filled(rect_casilla, color_fondo)

            arcade.draw_rect_outline(rect_casilla, arcade.color.BLACK, 2)
            
            # Número
            arcade.draw_text(
                str(num), x + CELL_SIZE/2, y + CELL_SIZE/2,
                arcade.color.BLACK, 24, anchor_x="center", anchor_y="center", bold=True
            )

        # 3. FICHAS
        for i, jugador in enumerate(self.jugadores):
            posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual)
            desplazamiento_x = (i % 2 - 0.5) * 20
            desplazamiento_y = (i // 2 - 0.5) * 20
            arcade.draw_circle_filled(posX + desplazamiento_x, posY + desplazamiento_y, jugador.radio, jugador.color)
            arcade.draw_circle_outline(posX + desplazamiento_x, posY + desplazamiento_y, jugador.radio, arcade.color.BLACK, 2)

        # 4. TEXTO
        nombres = ["ROJO", "AZUL", "AMARILLO", "MORADO"]
        texto = f"Turno: {nombres[self.turno_actual]} - Pulsa ESPACIO - (F11: Pantalla / ESC: Salir)"
        
        rect_texto = arcade.LBWH((self.width // 2) - 400, 35, 800, 50)
        arcade.draw_rect_filled(rect_texto, (0, 0, 0, 150))
        arcade.draw_text(
            texto, self.width // 2, 60, arcade.color.WHITE, 24, 
            anchor_x="center", anchor_y="center", bold=True
        )

def main():
    OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()