import arcade
import os
import urllib.request
import random
import math  # Librería para calcular distancias de clics
import json
import datetime

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
    os.path.join("assets", "img", "ficha", "Ficha_obra.png"),
    os.path.join("assets", "img", "ficha", "Ficha_estetica.png"),
    os.path.join("assets", "img", "ficha", "Ficha_informatica.png"),
    os.path.join("assets", "img", "ficha", "Ficha_madera.png")
]

# --- ESTADOS DEL JUEGO ---
ESTADO_MENU = 0                    
ESTADO_JUEGO = 1                   
ESTADO_NOMBRE = 2   # Pantalla para escribir el nombre

class Dado:
    def tirar(self):
        """Genera un número aleatorio entre 1 y 6 para el movimiento."""
        return random.randint(1,6)
    
dado = Dado()

class Ficha:
    def __init__(self, ID, image_path):
        """Inicializa los datos de cada jugador (ID, casilla actual, imagen)."""
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
        """Configura la ventana principal y prepara todas las variables iniciales del juego."""
        super().__init__(title=SCREEN_TITLE, fullscreen=True)
        
        self.set_mouse_visible(True)        
        self.estado = ESTADO_MENU           
        self.jugador_elegido = None         
        self.nombre = ""  # Variable para guardar tu nombre
        
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

        # --- PREGUNTAS: Variables de control ---
        self.mostrando_pregunta = False  
        self.pregunta_actual = None      
        self.botones_rects = []          
        self.resultado_quiz = None       
        self.tiempo_feedback = 0         
        self.lista_preguntas = []
        self.cargar_preguntas_json()
        
        # --- CONTROL DEL DADO VISUAL ---
        self.dado_animacion_activa = False
        self.dado_timer = 0.0
        self.dado_valor_final = 1

    def cargar_textura_ninja(self, url, nombre_temp, es_fondo):
        """Descarga una imagen de internet temporalmente."""
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

    def cargar_preguntas_json(self):
        """Lee el archivo JSON de preguntas."""
        self.lista_preguntas = []
        ruta_json = os.path.join("assets", "preguntas.json")
        if not os.path.exists(ruta_json): return
        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.lista_preguntas = datos.get("preguntas", [])
        except Exception as e:
            print(f"Error al leer JSON: {e}")

    def generar_espiral(self):
        """Calcula las posiciones en el tablero."""
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

    def activar_pregunta(self):
        """Filtra y activa la pantalla de preguntas."""
        self.mostrando_pregunta = True
        self.resultado_quiz = None
        categorias = ["Peluquería", "Estética", "Informática", "Madera"]
        categoria_elegida = categorias[self.jugador_elegido]

        preguntas_de_esta_categoria = []
        for bloque in self.lista_preguntas:
            if isinstance(bloque, dict) and bloque.get("categoria", "").lower() == categoria_elegida.lower():
                preguntas_de_esta_categoria = bloque.get("items", [])
                break
        
        if preguntas_de_esta_categoria:
            self.pregunta_actual = random.choice(preguntas_de_esta_categoria)
        
        self.botones_rects = []
        cx = self.width // 2
        cy = self.height // 2
        ancho_btn, alto_btn = 500, 60
        start_y = cy - 20
        for i in range(4):
            y = start_y - (i * 80)
            x = cx - (ancho_btn // 2)
            self.botones_rects.append((x, y, ancho_btn, alto_btn))

    def on_mouse_press(self, x, y, button, modifiers):
        """Control de clics para menú y preguntas."""
        if self.estado == ESTADO_MENU:
            for i in range(4):
                cx = self.width // 2 - 300 + (i * 200)
                cy = self.height // 2
                distancia = math.sqrt((x - cx)**2 + (y - cy)**2) 
                if distancia < 80:
                    self.jugador_elegido = i
                    self.turno_actual = i              
                    self.estado = ESTADO_NOMBRE 
        
        elif self.estado == ESTADO_JUEGO and self.mostrando_pregunta:
            if self.resultado_quiz is None:
                mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
                idx_correcto = mapa_letras.get(self.pregunta_actual["correcta"], 0)

                for i, rect in enumerate(self.botones_rects):
                    bx, by, bw, bh = rect
                    if bx < x < bx + bw and by < y < by + bh:
                        if i == idx_correcto:
                            self.resultado_quiz = "CORRECTO"
                            # --- TAREA: MOVIMIENTO SOLO SI ES CORRECTO ---
                            jugador = self.jugadores[self.jugador_elegido]
                            if jugador.casilla_actual + self.dado_valor_final <= 36:
                                jugador.casilla_actual += self.dado_valor_final
                            else:
                                jugador.casilla_actual = 36
                        else:
                            self.resultado_quiz = "INCORRECTO"
                            # Se queda donde está
                        return 
            else:
                self.mostrando_pregunta = False
                self.resultado_quiz = None

    def on_text(self, text):
        if self.estado == ESTADO_NOMBRE:
            if len(self.nombre) < 15 and text.isprintable() and text != '\r':
                self.nombre += text

    def on_update(self, delta_time):
        if self.resultado_quiz is not None:
            self.tiempo_feedback += delta_time
            if self.tiempo_feedback > 2.0:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0
                self.resultado_quiz = None

        if getattr(self, "dado_animacion_activa", False):
            self.dado_timer -= delta_time
            if self.dado_timer <= 0:
                self.dado_animacion_activa = False

    def on_key_press(self, key, modifiers):
        """Detecta teclas."""
        if self.estado == ESTADO_NOMBRE:
            if key == arcade.key.ENTER:
                if not self.nombre.strip(): self.nombre = "Jugador 1"
                self.estado = ESTADO_JUEGO
            elif key == arcade.key.BACKSPACE:
                self.nombre = self.nombre[:-1]
            return 
        
        if key == arcade.key.ESCAPE: self.close()
        elif key == arcade.key.F11: self.set_fullscreen(not self.fullscreen); self.set_mouse_visible(True)
            
        if self.estado == ESTADO_JUEGO and key == arcade.key.SPACE:
            if not self.mostrando_pregunta:
                # --- TAREA: TIRAR DADO Y PREPARAR PREGUNTA SIN MOVER AÚN ---
                self.dado_valor_final = dado.tirar()
                self.dado_animacion_activa = True
                self.dado_timer = 1.5
                
                if self.jugadores[self.jugador_elegido].casilla_actual < 36:
                    if self.lista_preguntas:
                        self.activar_pregunta()

    def on_draw(self):
        self.clear()
        if self.usar_imagen_fondo and self.background:
            arcade.draw_texture_rect(self.background, arcade.XYWH(self.width/2, self.height/2, self.width, self.height))

        if self.estado == ESTADO_MENU: self.dibujar_menu()
        elif self.estado == ESTADO_NOMBRE: self.dibujar_ingreso_nombre()
        elif self.estado == ESTADO_JUEGO: self.dibujar_tablero_y_fichas()
        
        if self.mostrando_pregunta and self.pregunta_actual: self.dibujar_capa_pregunta()
            
        if getattr(self, "dado_animacion_activa", False):
            cx, cy = self.width // 4, self.height // 2
            arcade.draw_rect_filled(arcade.XYWH(cx, cy, 250, 250), (0, 0, 0, 220))
            valor = random.randint(1, 6) if self.dado_timer > 0.5 else self.dado_valor_final
            texto = "TIRANDO..." if self.dado_timer > 0.5 else "¡RESULTADO!"
            color = arcade.color.WHITE if self.dado_timer > 0.5 else arcade.color.GOLD
            arcade.draw_text(str(valor), cx, cy - 20, color, 120, anchor_x="center", anchor_y="center", bold=True)
            arcade.draw_text(texto, cx, cy - 160, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center", bold=True)

    def dibujar_menu(self):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 150))
        arcade.draw_text("SELECCIONA TU CATEGORÍA", self.width//2, self.height//2 + 200, arcade.color.WHITE, 45, anchor_x="center", bold=True)
        nombres = ["OBRA", "ESTÉTICA", "INFORMÁTICA", "MADERA"]
        for i in range(4):
            cx, cy = self.width//2 - 300 + (i * 200), self.height//2
            if self.jugadores[i].texture: arcade.draw_texture_rect(self.jugadores[i].texture, arcade.XYWH(cx, cy, 120, 120))
            arcade.draw_text(nombres[i], cx, cy - 100, arcade.color.WHITE, 18, anchor_x="center", bold=True)

    def dibujar_ingreso_nombre(self):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 180))
        arcade.draw_text("INTRODUCE TU NOMBRE:", self.width//2, self.height//2 + 50, arcade.color.WHITE, 35, anchor_x="center", bold=True)
        arcade.draw_text(self.nombre + "_", self.width//2, self.height//2 - 20, arcade.color.GOLD, 45, anchor_x="center", bold=True)

    def dibujar_tablero_y_fichas(self):
        off_x, off_y = self.obtener_offsets()
        for col, fila, num in self.camino:
            x, y = off_x + col * (CELL_SIZE + MARGIN), off_y - fila * (CELL_SIZE + MARGIN)
            color = arcade.color.GOLD if num % 5 == 0 else (arcade.color.INDIAN_RED if num == 36 else arcade.color.GREEN)
            arcade.draw_rect_filled(arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE), color)
            arcade.draw_text(str(num), x + CELL_SIZE/2, y + CELL_SIZE/2, arcade.color.BLACK, 24, anchor_x="center", bold=True)
        
        jugador = self.jugadores[self.jugador_elegido]
        posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual)
        if jugador.texture: arcade.draw_texture_rect(jugador.texture, arcade.XYWH(posX, posY, 60, 60))
        arcade.draw_text("TÚ", posX, posY + 45, arcade.color.WHITE, 14, anchor_x="center", bold=True)

    def dibujar_capa_pregunta(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 230))
        cx, cy = self.width//2, self.height//2
        arcade.draw_text(self.pregunta_actual["pregunta"], cx, cy + 150, arcade.color.WHITE, 30, anchor_x="center", anchor_y="center", width=900, align="center", multiline=True, bold=True)
        colores = [arcade.color.BLUE, arcade.color.RED, arcade.color.AMBER, arcade.color.GREEN]
        mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
        idx_cor = mapa_letras.get(self.pregunta_actual["correcta"], 0)
        for i, rect in enumerate(self.botones_rects):
            x, y, w, h = rect
            color = colores[i]
            if self.resultado_quiz: color = arcade.color.GOLD if i == idx_cor else arcade.color.GRAY
            arcade.draw_lbwh_rectangle_filled(x, y, w, h, color)
            txt_color = arcade.color.BLACK if color in [arcade.color.GOLD, arcade.color.AMBER, arcade.color.GREEN] else arcade.color.WHITE
            arcade.draw_text(f"{['A','B','C','D'][i]}) {self.pregunta_actual['opciones'][i]}", x+w/2, y+h/2, txt_color, 18, anchor_x="center", anchor_y="center")
        if self.resultado_quiz:
            txt, col = ("¡CORRECTO!", arcade.color.GREEN) if self.resultado_quiz == "CORRECTO" else ("¡FALLASTE!", arcade.color.RED)
            arcade.draw_text(txt, cx, cy + 300, col, 40, anchor_x="center", bold=True)

def main(): OcaGame(); arcade.run()
if __name__ == "__main__": main()