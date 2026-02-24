import arcade
import os
import urllib.request
import random
import math  ## CAMBIO: Nueva librería para calcular distancias de clics

# --- 1. CONFIGURACIÓN ---
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

# --- 2. CONSTANTES ---
SCREEN_TITLE = "La Oca - Versión Master (F11 para Pantalla Completa)"
URL_FONDO = "https://i.postimg.cc/Qx0fKVpd/Fondo-Tablero.jpg"
URL_CASILLA_1 = "https://i.postimg.cc/Sxh5FjWh/bandera.png"

CELL_SIZE = 120
MARGIN = 5

PLAYER_IMAGES = [
    os.path.join("assets", "img", "ficha", "Ficha_Arte-sinfondo.png"),
    os.path.join("assets", "img", "ficha", "FICHA_CIENCIA-sinfondo.png"),
    os.path.join("assets", "img", "ficha", "Ficha_Historia-sinfondo.png"),
    os.path.join("assets", "img", "ficha", "Ficha_Geografia-sinfondo.png")
]

# --- NUEVOS ESTADOS DEL JUEGO --- ## CAMBIO: Definición de pantallas
ESTADO_MENU = 0                     ## CAMBIO: Etiqueta para el menú
ESTADO_JUEGO = 1                    ## CAMBIO: Etiqueta para el tablero

class Dado:
    def tirar(self):
        return random.randint(1,6)
    
dado = Dado()

class Ficha:
    def __init__(self, ID, image_path):
        self.ID = ID
        self.casilla_actual = 0
        self.radio = 25
        self.texture = None
        try:
            self.texture = arcade.load_texture(image_path)
        except Exception as e:
            print(f"Error carga imagen {ID}: {e}")

class OcaGame(arcade.Window):
    def __init__(self):
        super().__init__(title=SCREEN_TITLE, fullscreen=True)
        
        self.set_mouse_visible(True)        ## CAMBIO: Forzar cursor visible
        self.estado = ESTADO_MENU           ## CAMBIO: El juego arranca en el menú
        self.jugador_elegido = None         ## CAMBIO: Variable para guardar tu ficha
        
        self.background = None
        self.usar_imagen_fondo = False
        self.textura_casilla_1 = None 

        print("Cargando recursos... ⚙️")
        self.cargar_textura_ninja(URL_FONDO, "temp_fondo.jpg", es_fondo=True)
        self.cargar_textura_ninja(URL_CASILLA_1, "temp_c1.png", es_fondo=False)

        self.camino = []
        self.generar_espiral()
        self.jugadores = [Ficha(i, PLAYER_IMAGES[i]) for i in range(4)]
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
            if os.path.exists(nombre_temp): os.remove(nombre_temp)
        except Exception:
            if es_fondo: self.background_color = arcade.color.GRAY

    def generar_espiral(self):
        total_casillas = 36
        col_inicio, col_fin, fila_inicio, fila_fin = 0, 5, 0, 5
        n = 1
        while n <= total_casillas:
            for i in range(col_inicio, col_fin + 1):
                if n > total_casillas: break
                self.camino.append((i, fila_inicio, n)); n += 1
            fila_inicio += 1
            for i in range(fila_inicio, fila_fin + 1):
                if n > total_casillas: break
                self.camino.append((col_fin, i, n)); n += 1
            col_fin -= 1
            for i in range(col_fin, col_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((i, fila_fin, n)); n += 1
            fila_fin -= 1
            for i in range(fila_fin, fila_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((col_inicio, i, n)); n += 1
            col_inicio += 1

    def obtener_offsets(self):
        tablero_ancho = 6 * (CELL_SIZE + MARGIN)
        tablero_alto = 6 * (CELL_SIZE + MARGIN)
        off_x = (self.width - tablero_ancho) // 2
        off_y = (self.height // 2) + (tablero_alto // 2) - CELL_SIZE - 110
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

    ## --- BLOQUE NUEVO ---
    def on_mouse_press(self, x, y, button, modifiers):  ## CAMBIO: Función nueva para clics
        if self.estado == ESTADO_MENU:                  ## CAMBIO: Solo funciona en el menú
            for i in range(4):
                cx = self.width // 2 - 300 + (i * 200)
                cy = self.height // 2
                # Pitágoras para detectar clic manual
                distancia = math.sqrt((x - cx)**2 + (y - cy)**2) 
                if distancia < 80:                      ## CAMBIO: Si pulsas una ficha...
                    self.jugador_elegido = i            ## CAMBIO: Guardar selección
                    self.estado = ESTADO_JUEGO          ## CAMBIO: Cambiar al tablero
                    print(f"Elegido: {i}")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.close()
        elif key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            self.set_mouse_visible(True)
            
        # CAMBIO: Se añade la condición de que el estado sea JUEGO para tirar el dado
        if self.estado == ESTADO_JUEGO and key == arcade.key.SPACE:
            jugador = self.jugadores[self.turno_actual]
            pasos = dado.tirar()
            if jugador.casilla_actual < 36:
                jugador.casilla_actual += pasos
            self.turno_actual = (self.turno_actual + 1) % 4

    def on_draw(self):
        self.clear()
        if self.usar_imagen_fondo and self.background:
            arcade.draw_texture_rect(self.background, arcade.XYWH(self.width / 2, self.height / 2, self.width, self.height))

        # --- CAMBIO: Lógica para elegir qué dibujar ---
        if self.estado == ESTADO_MENU:
            self.dibujar_menu()             ## CAMBIO: Llamada a la nueva pantalla
        else:
            self.dibujar_tablero_y_fichas() ## CAMBIO: Llamada a la lógica original

    ## --- FUNCIÓN NUEVA ---
    def dibujar_menu(self):                 ## CAMBIO: Bloque nuevo para la visual del menú
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 150))
        arcade.draw_text("SELECCIONA TU CATEGORÍA", self.width // 2, self.height // 2 + 200,
                         arcade.color.WHITE, 45, anchor_x="center", bold=True)
        
        nombres = ["ARTE", "CIENCIA", "HISTORIA", "GEOGRAFÍA"]
        for i in range(4):
            cx = self.width // 2 - 300 + (i * 200)
            cy = self.height // 2
            if self.jugadores[i].texture:
                arcade.draw_texture_rect(self.jugadores[i].texture, arcade.XYWH(cx, cy, 120, 120))
            arcade.draw_text(nombres[i], cx, cy - 100, arcade.color.WHITE, 18, anchor_x="center", bold=True)

    def dibujar_tablero_y_fichas(self):
        off_x, off_y = self.obtener_offsets()
        for col, fila, num in self.camino:
            x, y = off_x + col * (CELL_SIZE + MARGIN), off_y - fila * (CELL_SIZE + MARGIN)
            rect_casilla = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE)
            if num == 1 and self.textura_casilla_1:
                arcade.draw_texture_rect(self.textura_casilla_1, rect_casilla)
            else:
                color_fondo = arcade.color.GOLD if num % 5 == 0 else (arcade.color.INDIAN_RED if num == 36 else arcade.color.GREEN)
                arcade.draw_rect_filled(rect_casilla, color_fondo)
            arcade.draw_rect_outline(rect_casilla, arcade.color.BLACK, 2)
            arcade.draw_text(str(num), x + CELL_SIZE/2, y + CELL_SIZE/2, arcade.color.BLACK, 24, anchor_x="center", bold=True)

        for i, jugador in enumerate(self.jugadores):
            posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual)
            dx, dy = (i % 2 - 0.5) * 40, (i // 2 - 0.5) * 40
            if jugador.texture:
                arcade.draw_texture_rect(jugador.texture, arcade.XYWH(posX + dx, posY + dy, 60, 60))
            
            # --- CAMBIO: Bloque nuevo para indicar quién es el jugador ---
            if i == self.jugador_elegido:
                arcade.draw_text("TÚ", posX + dx, posY + dy + 45, arcade.color.WHITE, 14, anchor_x="center", bold=True)

        nombres = ["Arte", "Ciencia", "Historia", "Geografía"]
        texto = f"Turno: {nombres[self.turno_actual]} - Pulsa ESPACIO"
        arcade.draw_text(texto, self.width // 2, 60, arcade.color.WHITE, 24, anchor_x="center", bold=True)

def main():
    OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()