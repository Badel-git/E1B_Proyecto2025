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
URL_FONDO = "https://i.postimg.cc/2ywynnLw/Fondo-Nuevo.jpg"
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
ESTADO_ERROR_FATAL = 3 # NUEVO: Pantalla de bloqueo si falla el JSON
ESTADO_VICTORIA = 4

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
        self.tiempo_error = 0.0 # NUEVO: Temporizador para el cierre del juego
        
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
        self.contador_tiradas = 0
        self.casillas_penalizacion = [9, 18, 26]
        self.casillas_turbo = [5, 14, 22]

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

        # --- ANIMACIÓN DE VICTORIA ---
        self.animacion_victoria = 0

    def cargar_textura_ninja(self, url, nombre_temp, es_fondo):
        """Descarga una imagen de internet temporalmente para usarla en el juego y luego borra el archivo."""
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
        """Lee el archivo JSON. Si falla, activa el bloqueo fatal en pantalla."""
        self.lista_preguntas = []
        ruta_json = os.path.join("assets", "preguntas.json")

        if not os.path.exists(ruta_json):
            self.estado = ESTADO_ERROR_FATAL # Activa el bloqueo fatal
            return

        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.lista_preguntas = datos.get("preguntas", [])
                
            if len(self.lista_preguntas) == 0:
                self.estado = ESTADO_ERROR_FATAL 
            else:
                print(f"[OK] Se han cargado {len(self.lista_preguntas)} categorías de preguntas.")

        except Exception as e:
            print(f"[ERROR] Fallo al leer el JSON: {e}")
            self.estado = ESTADO_ERROR_FATAL 

    def cargar_ranking(self):
        """Lee el archivo de puntuaciones. Si no existe, devuelve una lista vacía."""
        ruta_ranking = os.path.join("assets", "ranking.json")
        if not os.path.exists(ruta_ranking):
            return []
            
        try:
            with open(ruta_ranking, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except Exception:
            return []
        
    def guardar_puntuacion(self, nombre, categoria, tiradas):
        """Guarda la puntuación de un jugador al finalizar la partida en el archivo de ranking."""
        ranking = self.cargar_ranking()
        nuevo_record = {
            "nombre": nombre,
            "categoria": categoria,
            "tiradas": tiradas,
            "fecha": str(datetime.date.today())
        }
        ranking.append(nuevo_record)
        
        ruta_ranking = os.path.join("assets", "ranking.json")
        try:
            # Nos aseguramos de que la carpeta assets existe
            if not os.path.exists("assets"):
                os.makedirs("assets")
            with open(ruta_ranking, "w", encoding="utf-8") as archivo:
                json.dump(ranking, archivo, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar puntuación: {e}")

    def obtener_top_10(self):
        """Devuelve los 10 mejores jugadores ordenados por el menor número de tiradas."""
        ranking = self.cargar_ranking()
        ranking.sort(key=lambda x: x['tiradas'])
        return ranking[:10]

    def generar_espiral(self):
        """Calcula matemáticamente las posiciones en el tablero para formar una espiral de 36 casillas."""
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
        """Calcula el margen para centrar el tablero perfectamente en la pantalla."""
        tablero_ancho = 6 * (CELL_SIZE + MARGIN)
        tablero_alto = 6 * (CELL_SIZE + MARGIN)
        off_x = (self.width - tablero_ancho) // 2
        off_y = (self.height // 2) + (tablero_alto // 2) - CELL_SIZE - 110
        return off_x, off_y

    def obtener_coordenadas_casilla(self, numero_casilla):
        """Devuelve las coordenadas exactas X e Y de la pantalla donde debe dibujarse una casilla concreta."""
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
        """Filtra la pregunta según la categoría de la ficha del jugador y prepara la pantalla."""
        self.mostrando_pregunta = True
        self.resultado_quiz = None
        
        categorias = ["Obra", "Imagen personal", "Informática", "Madera"]
        categoria_elegida = categorias[self.jugador_elegido]

        preguntas_de_esta_categoria = []
        for bloque in self.lista_preguntas:
            if isinstance(bloque, dict) and bloque.get("categoria", "").lower() == categoria_elegida.lower():
                preguntas_de_esta_categoria = bloque.get("items", [])
                break
        
        if preguntas_de_esta_categoria:
            self.pregunta_actual = random.choice(preguntas_de_esta_categoria)
        else:
            self.pregunta_actual = {
                "pregunta": f"Error: No se encontraron preguntas para {categoria_elegida}", 
                "opciones": ["A", "B", "C", "D"], 
                "correcta": "A"
            }
        
        self.botones_rects = []
        cx, cy = self.width // 2, self.height // 2
        ancho_btn, alto_btn = 500, 60
        start_y = cy - 20
        
        for i in range(4):
            y = start_y - (i * 80)
            x = cx - (ancho_btn // 2)
            self.botones_rects.append((x, y, ancho_btn, alto_btn))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.estado == ESTADO_ERROR_FATAL: return

        if self.estado == ESTADO_MENU:
            for i in range(4):
                cx, cy = self.width // 2 - 300 + (i * 200), self.height // 2
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
                        self.resultado_quiz = "CORRECTO" if i == idx_correcto else "INCORRECTO"
                        return 
            else:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0 
                self.resultado_quiz = None

    def on_text(self, text):
        if self.estado == ESTADO_NOMBRE:
            if len(self.nombre) < 15 and text.isprintable() and text != '\r':
                self.nombre += text

    def on_update(self, delta_time):
        if self.estado == ESTADO_ERROR_FATAL:
            self.tiempo_error += delta_time
            if self.tiempo_error >= 10.0: self.close()
            return

        if self.resultado_quiz is not None:
            self.tiempo_feedback += delta_time
            if self.tiempo_feedback > 2.0:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0
                self.resultado_quiz = None

        if self.dado_animacion_activa:
            self.dado_timer -= delta_time
            if self.dado_timer <= 0: self.dado_animacion_activa = False

        if self.estado == ESTADO_VICTORIA:
            self.animacion_victoria += delta_time * 3

    def on_key_press(self, key, modifiers):
        if self.estado == ESTADO_ERROR_FATAL: return

        # --- AÑADIDO: REINICIO DESDE VICTORIA ---
        if self.estado == ESTADO_VICTORIA: 
            if key == arcade.key.ENTER:
                self.estado = ESTADO_MENU
                self.nombre = ""
                self.contador_tiradas = 0
                for f in self.jugadores: f.casilla_actual = 0
            return
        
        if self.estado == ESTADO_NOMBRE:
            if key == arcade.key.ENTER:
                if not self.nombre.strip(): self.nombre = "Jugador 1"
                self.estado = ESTADO_JUEGO
            elif key == arcade.key.BACKSPACE: self.nombre = self.nombre[:-1]
            return 
        
        if key == arcade.key.ESCAPE: self.close()
        elif key == arcade.key.F11: self.set_fullscreen(not self.fullscreen)
            
        if self.estado == ESTADO_JUEGO and key == arcade.key.SPACE and not self.mostrando_pregunta:
            jugador = self.jugadores[self.jugador_elegido] 
            pasos = dado.tirar()
            self.contador_tiradas += 1
            self.dado_animacion_activa, self.dado_timer, self.dado_valor_final = True, 1.5, pasos
            
            jugador.casilla_actual += pasos
            
            # --- CORRECCIÓN CLAVE: LLEGADA A META ---
            if jugador.casilla_actual >= 36:
                jugador.casilla_actual = 36
                self.comprobar_victoria()
                return # IMPORTANTE: Detener ejecución aquí para que se pinte la victoria

            # Penalización / Turbo (Solo si no ha ganado ya)
            if jugador.casilla_actual in self.casillas_penalizacion:
                jugador.casilla_actual = max(1, jugador.casilla_actual - 3)
            elif jugador.casilla_actual in self.casillas_turbo:
                jugador.casilla_actual = min(36, jugador.casilla_actual + 5)
                if jugador.casilla_actual == 36:
                    self.comprobar_victoria()
                    return

            # Pregunta
            if 0 < jugador.casilla_actual < 36 and len(self.lista_preguntas) > 0:
                self.activar_pregunta()

    def on_draw(self):
        self.clear()
        if self.usar_imagen_fondo and self.background:
            arcade.draw_texture_rect(self.background, arcade.XYWH(self.width / 2, self.height / 2, self.width, self.height))

        if self.estado == ESTADO_ERROR_FATAL: self.dibujar_error_fatal()
        elif self.estado == ESTADO_MENU: self.dibujar_menu()            
        elif self.estado == ESTADO_NOMBRE: self.dibujar_ingreso_nombre()
        elif self.estado == ESTADO_JUEGO:
            self.dibujar_tablero_y_fichas()
            if self.mostrando_pregunta and self.pregunta_actual: self.dibujar_capa_pregunta()
            if self.dado_animacion_activa: self.dibujar_dado_visual()
        elif self.estado == ESTADO_VICTORIA:
            self.dibujar_victoria()

    def dibujar_dado_visual(self):
        cx, cy = self.width // 4, self.height // 2
        arcade.draw_rect_filled(arcade.XYWH(cx, cy, 250, 250), (0, 0, 0, 220))
        arcade.draw_rect_outline(arcade.XYWH(cx, cy, 250, 250), arcade.color.WHITE, 5)
        v = random.randint(1, 6) if self.dado_timer > 0.5 else self.dado_valor_final
        txt, col = ("TIRANDO...", arcade.color.WHITE) if self.dado_timer > 0.5 else ("¡RESULTADO!", arcade.color.GOLD)
        arcade.draw_text(str(v), cx, cy - 20, col, 120, anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text(txt, cx, cy - 160, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center", bold=True)

    def dibujar_error_fatal(self):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), arcade.color.BLACK)
        arcade.draw_text("⚠️ ERROR ⚠️", self.width // 2, self.height // 2 + 100, arcade.color.RED, 50, anchor_x="center", bold=True)
        arcade.draw_text("Falta el archivo de preguntas", self.width // 2, self.height // 2, arcade.color.WHITE, 30, anchor_x="center", bold=True)

    def dibujar_menu(self):                
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 150))
        arcade.draw_text("SELECCIONA TU CATEGORÍA", self.width // 2, self.height // 2 + 200, arcade.color.WHITE, 45, anchor_x="center", bold=True)
        nombres = ["OBRA", "IMAGEN PERSONAL", "INFORMÁTICA", "MADERA"]
        for i in range(4):
            cx, cy = self.width // 2 - 300 + (i * 200), self.height // 2
            if self.jugadores[i].texture: arcade.draw_texture_rect(self.jugadores[i].texture, arcade.XYWH(cx, cy, 120, 120))
            arcade.draw_text(nombres[i], cx, cy - 100, arcade.color.WHITE, 18, anchor_x="center", bold=True)

    def dibujar_ingreso_nombre(self):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 180))
        arcade.draw_text("INTRODUCE TU NOMBRE:", self.width // 2, self.height // 2 + 50, arcade.color.WHITE, 35, anchor_x="center", bold=True)
        arcade.draw_text(self.nombre + "_", self.width // 2, self.height // 2 - 20, arcade.color.GOLD, 45, anchor_x="center", bold=True)

    def dibujar_tablero_y_fichas(self):
        off_x, off_y = self.obtener_offsets()
        for col, fila, num in self.camino:
            x, y = off_x + col * (CELL_SIZE + MARGIN), off_y - fila * (CELL_SIZE + MARGIN)
            rect = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE)
            if num == 1 and self.textura_casilla_1: arcade.draw_texture_rect(self.textura_casilla_1, rect)
            else:
                c = arcade.color.RED if num in self.casillas_penalizacion else arcade.color.BLUE if num in self.casillas_turbo else arcade.color.ORANGE if num == 36 else arcade.color.GREEN
                arcade.draw_rect_filled(rect, c)
            arcade.draw_rect_outline(rect, arcade.color.BLACK, 2)
            arcade.draw_text(str(num), x + CELL_SIZE/2, y + CELL_SIZE/2, arcade.color.BLACK, 24, anchor_x="center", bold=True)

        j = self.jugadores[self.jugador_elegido]
        posX, posY = self.obtener_coordenadas_casilla(j.casilla_actual)
        if j.texture: arcade.draw_texture_rect(j.texture, arcade.XYWH(posX, posY, 60, 60))
        arcade.draw_text(f"Jugador: {self.nombre}", 20, self.height - 40, arcade.color.WHITE, 22, bold=True)

    def dibujar_capa_pregunta(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 230))
        cx, cy = self.width // 2, self.height // 2
        arcade.draw_text(self.pregunta_actual["pregunta"], cx, cy + 150, arcade.color.WHITE, 30, anchor_x="center", anchor_y="center", width=900, align="center", multiline=True, bold=True)
        letras = ["A", "B", "C", "D"]
        colores = [arcade.color.BLUE, arcade.color.RED, arcade.color.AMBER, arcade.color.GREEN]
        idx_corr = {"A": 0, "B": 1, "C": 2, "D": 3}.get(self.pregunta_actual["correcta"], 0)
        for i, rect in enumerate(self.botones_rects):
            x, y, w, h = rect
            c_btn = colores[i]
            if self.resultado_quiz: c_btn = arcade.color.GOLD if i == idx_corr else arcade.color.GRAY
            arcade.draw_lbwh_rectangle_filled(x, y, w, h, c_btn)
            arcade.draw_text(f"{letras[i]}) {self.pregunta_actual['opciones'][i]}", x + w/2, y + h/2, arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")
        if self.resultado_quiz:
            txt, col = ("¡CORRECTO!", arcade.color.GREEN) if self.resultado_quiz == "CORRECTO" else ("¡FALLASTE!", arcade.color.RED)
            arcade.draw_text(txt, cx, cy + 300, col, 40, anchor_x="center", bold=True)

    def comprobar_victoria(self):
        self.estado = ESTADO_VICTORIA
        self.mostrando_pregunta = False
        categorias = ["Obra", "Imagen personal", "Informática", "Madera"]
        self.guardar_puntuacion(self.nombre, categorias[self.jugador_elegido], self.contador_tiradas)

    def dibujar_victoria(self):
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 240))
        escala = 50 + math.sin(self.animacion_victoria) * 5
        arcade.draw_text("🎉 ¡HAS GANADO! 🎉", self.width // 2, self.height - 150, arcade.color.GOLD, escala, anchor_x="center", bold=True)
        arcade.draw_text(f"{self.nombre} terminó en {self.contador_tiradas} tiradas", self.width // 2, self.height - 230, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("🏆 TOP 10 JUGADORES 🏆", self.width // 2, self.height - 320, arcade.color.WHITE, 35, anchor_x="center")
        top10, y = self.obtener_top_10(), self.height - 380
        medallas = ["🥇", "🥈", "🥉"]
        for i, jug in enumerate(top10):
            pref = medallas[i] if i < 3 else f"{i+1}."
            arcade.draw_text(f"{pref} {jug['nombre']} - {jug['tiradas']} tiradas", self.width // 2, y, arcade.color.WHITE, 22, anchor_x="center")
            y -= 35
        arcade.draw_text("Pulsa ENTER para volver al menú principal", self.width // 2, 80, arcade.color.GRAY, 18, anchor_x="center")

def main():
    OcaGame()
    arcade.run()

if __name__ == "__main__":
    main()