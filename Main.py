import arcade
import os
import urllib.request
import random
import math  ## CAMBIO: Nueva librería para calcular distancias de clics
import json

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

    # --- REINTEGRACIÓN PREGUNTAS: Variables de control ---
        # ========================================================
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


        # --- REINTEGRACIÓN PREGUNTAS: Cargar JSON ---
    def cargar_preguntas_json(self):
        try:
           ruta_json = os.path.join("assets", "preguntas.json")
           with open(ruta_json, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.lista_preguntas = datos["preguntas"]
                print(f"¡Éxito! Se han cargado {len(self.lista_preguntas)} preguntas.")
        except Exception as e:
            print(f"ERROR cargando JSON: {e}")
            self.lista_preguntas = [{"pregunta": "Error: No se leyó preguntas.json", "opciones": ["A", "B", "C", "D"], "correcta": "A"}]

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


    # --- REINTEGRACIÓN PREGUNTAS: Preparar la pregunta ---
    def activar_pregunta(self):
        self.mostrando_pregunta = True
        self.resultado_quiz = None
        
        if self.lista_preguntas:
            self.pregunta_actual = random.choice(self.lista_preguntas)
        
        self.botones_rects = []
        cx = self.width // 2
        cy = self.height // 2
        ancho_btn, alto_btn = 500, 60
        start_y = cy - 20
        
        for i in range(4):
            y = start_y - (i * 80)
            x = cx - (ancho_btn // 2)
            self.botones_rects.append((x, y, ancho_btn, alto_btn))

    ## --- BLOQUE NUEVO ---
    def on_mouse_press(self, x, y, button, modifiers):
        if self.estado == ESTADO_MENU:
            for i in range(4):
                cx = self.width // 2 - 300 + (i * 200)
                cy = self.height // 2
                # Pitágoras para detectar clic manual
                distancia = math.sqrt((x - cx)**2 + (y - cy)**2) 
                if distancia < 80:
                    self.jugador_elegido = i
                    self.turno_actual = i               ## CAMBIO: Forzamos que el turno inicial sea el de tu ficha
                    self.estado = ESTADO_JUEGO
                    print(f"Elegido: {i}")
        
        elif self.estado == ESTADO_JUEGO and self.mostrando_pregunta:
            if self.resultado_quiz is None:
                mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
                idx_correcto = mapa_letras.get(self.pregunta_actual["correcta"], 0)

                for i, rect in enumerate(self.botones_rects):
                    bx, by, bw, bh = rect
                    if bx < x < bx + bw and by < y < by + bh:
                        if i == idx_correcto:
                            self.resultado_quiz = "CORRECTO"
                        else:
                            self.resultado_quiz = "INCORRECTO"
                        return 
            else:
                # Cierra la ventana si ya respondiste y haces clic
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0 
                self.resultado_quiz = None

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
        if key == arcade.key.ESCAPE:
            self.close()
        elif key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            self.set_mouse_visible(True)
            
        # CAMBIO: Solo movemos la ficha seleccionada y eliminamos el cambio de turno
        if self.estado == ESTADO_JUEGO and key == arcade.key.SPACE:
            if not self.mostrando_pregunta:
                jugador = self.jugadores[self.jugador_elegido] 
                pasos = dado.tirar()
                self.dado_animacion_activa = True
                self.dado_timer = 1.5
                self.dado_valor_final = pasos
                
                if jugador.casilla_actual < 36:
                    jugador.casilla_actual += pasos
                
                # Lanzar pregunta si se mueve (y no es la meta ni el inicio)
                if 0 < jugador.casilla_actual < 36:
                    self.activar_pregunta()
                    
            # Si la pregunta está abierta y respondida, ESPACIO la cierra
            elif self.mostrando_pregunta and self.resultado_quiz is not None:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0
                self.resultado_quiz = None

    def on_draw(self):
        self.clear()
        if self.usar_imagen_fondo and self.background:
            arcade.draw_texture_rect(self.background, arcade.XYWH(self.width / 2, self.height / 2, self.width, self.height))

        # --- CAMBIO: Lógica para elegir qué dibujar ---
        if self.estado == ESTADO_MENU:
            self.dibujar_menu()             ## CAMBIO: Llamada a la nueva pantalla
        else:
            self.dibujar_tablero_y_fichas() ## CAMBIO: Llamada a la lógica original
        
        if self.mostrando_pregunta and self.pregunta_actual:
            self.dibujar_capa_pregunta()
        if getattr(self, "dado_animacion_activa", False):
                    cx = self.width // 4
                    cy = self.height // 2
                    
                    arcade.draw_rect_filled(arcade.XYWH(cx, cy, 250, 250), (0, 0, 0, 220))
                    arcade.draw_rect_outline(arcade.XYWH(cx, cy, 250, 250), arcade.color.WHITE, 5)
                    
                    if self.dado_timer > 0.5:
                        valor_mostrar = random.randint(1, 6)
                        texto_dado = "TIRANDO..."
                        color_texto = arcade.color.WHITE
                    else:
                        valor_mostrar = self.dado_valor_final
                        texto_dado = "¡RESULTADO!"
                        color_texto = arcade.color.GOLD
                        
                    arcade.draw_text(str(valor_mostrar), cx, cy - 20, color_texto, 
                                    120, anchor_x="center", anchor_y="center", bold=True)
                    
                    arcade.draw_text(texto_dado, cx, cy - 160, arcade.color.WHITE, 
                                    24, anchor_x="center", anchor_y="center", bold=True)
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
            if i == self.jugador_elegido: ## CAMBIO: Condición para dibujar solo a tu jugador
                posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual)
                dx, dy = 0, 0 ## CAMBIO: Centramos la ficha anulando el desfase
                if jugador.texture:
                    arcade.draw_texture_rect(jugador.texture, arcade.XYWH(posX + dx, posY + dy, 60, 60))
                
                # --- CAMBIO: Bloque nuevo para indicar quién es el jugador ---
                arcade.draw_text("TÚ", posX + dx, posY + dy + 45, arcade.color.WHITE, 14, anchor_x="center", bold=True)

        nombres = ["Arte", "Ciencia", "Historia", "Geografía"]
        texto = f"Turno: {nombres[self.jugador_elegido]} - Pulsa ESPACIO" ## CAMBIO: Mostrar solo tu nombre
        arcade.draw_text(texto, self.width // 2, 60, arcade.color.WHITE, 24, anchor_x="center", bold=True)

        nombres = ["Arte", "Ciencia", "Historia", "Geografía"]
        texto = f"Turno: {nombres[self.turno_actual]} - Pulsa ESPACIO"
        arcade.draw_text(texto, self.width // 2, 60, arcade.color.WHITE, 24, anchor_x="center", bold=True)
    
    def dibujar_capa_pregunta(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 230))
        cx = self.width // 2
        cy = self.height // 2

        arcade.draw_text(
            self.pregunta_actual["pregunta"], cx, cy + 150, arcade.color.WHITE,
            30, anchor_x="center", anchor_y="center", width=900, align="center", multiline=True, bold=True
        )

        letras = ["A", "B", "C", "D"]
        colores_base = [arcade.color.BLUE, arcade.color.RED, arcade.color.AMBER, arcade.color.GREEN]
        mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
        idx_correcto = mapa_letras.get(self.pregunta_actual["correcta"], 0)

        for i, rect in enumerate(self.botones_rects):
            x, y, w, h = rect
            color_btn = colores_base[i]
            
            if self.resultado_quiz is not None:
                if i == idx_correcto:
                    color_btn = arcade.color.GOLD  
                else:
                    color_btn = arcade.color.GRAY  
            
            arcade.draw_lbwh_rectangle_filled(x, y, w, h, color_btn)
            arcade.draw_lbwh_rectangle_outline(x, y, w, h, arcade.color.WHITE, 3)
            
            if color_btn in (arcade.color.GOLD, arcade.color.AMBER, arcade.color.GREEN, arcade.color.YELLOW):
                color_texto = arcade.color.BLACK
            else:
                color_texto = arcade.color.WHITE

            texto_op = f"{letras[i]}) {self.pregunta_actual['opciones'][i]}"
            arcade.draw_text(texto_op, x + w / 2, y + h / 2, color_texto, 18, anchor_x="center", anchor_y="center")

        if self.resultado_quiz:
            texto_res = "¡CORRECTO!" if self.resultado_quiz == "CORRECTO" else "¡FALLASTE!"
            color_res = arcade.color.GREEN if self.resultado_quiz == "CORRECTO" else arcade.color.RED
            
            arcade.draw_text(texto_res, cx + 2, cy - 252, arcade.color.BLACK, 40, anchor_x="center", bold=True)
            arcade.draw_text(texto_res, cx - 2, cy - 248, arcade.color.BLACK, 40, anchor_x="center", bold=True)
            arcade.draw_text(texto_res, cx, cy - 250, color_res, 40, anchor_x="center", bold=True)

def main():
    OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()