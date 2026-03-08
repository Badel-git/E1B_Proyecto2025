# =====================================================================
# 1. HERRAMIENTAS EXTERNAS (Importaciones)
# =====================================================================
import arcade          # Traemos la caja de herramientas principal para crear videojuegos (gráficos, ventanas).
import os              # Traemos la herramienta para hablar con el sistema operativo (Windows/Mac) y buscar archivos.
import urllib.request  # Traemos la herramienta para poder descargar cosas de Internet.
import random          # Traemos la herramienta para generar cosas al azar (como tirar unos dados).
import math            # Traemos la calculadora matemática del ordenador (para medir distancias).
import json            # Traemos un traductor para poder leer archivos de texto llenos de datos (las preguntas).
import datetime        # Traemos un reloj y calendario para saber qué día es hoy.

# =====================================================================
# 2. PREPARAR EL TERRENO (¿Dónde estamos?)
# =====================================================================
# Averiguamos en qué carpeta exacta de tu ordenador está guardado este archivo de código.
file_path = os.path.dirname(os.path.abspath(__file__))
# Le decimos al ordenador: "Quédate en esta carpeta, todo lo que busques estará aquí".
os.chdir(file_path)

# =====================================================================
# 3. REGLAS FIJAS (Constantes que nunca cambian)
# =====================================================================
# El texto que saldrá en la barrita de arriba de la ventana del juego.
SCREEN_TITLE = "La Oca - Versión Master (F11 para Pantalla Completa)"
# Un enlace de internet por si queremos descargar una imagen de fondo.
URL_FONDO = "https://i.postimg.cc/2ywynnLw/Fondo-Nuevo.jpg"

CELL_SIZE = 120 # El tamaño en píxeles que tendrá cada cuadrado (casilla) del tablero.
MARGIN = 5      # El espacio en píxeles de separación entre una casilla y otra.

# Creamos una lista con las direcciones (rutas) de los dibujos de las 4 fichas de los jugadores.
PLAYER_IMAGES = [
    os.path.join("assets", "img", "ficha", "Ficha_obra.png"),
    os.path.join("assets", "img", "ficha", "Ficha_estetica.png"),
    os.path.join("assets", "img", "ficha", "Ficha_informatica.png"),
    os.path.join("assets", "img", "ficha", "Ficha_madera.png")
]

# --- PANTALLAS DEL JUEGO (Estados) ---
# Usamos números simples para decirle al juego qué "pantalla" debe mostrar en cada momento.
ESTADO_MENU = 0        # Pantalla 0: Menú principal.
ESTADO_JUEGO = 1       # Pantalla 1: El tablero de juego.
ESTADO_NOMBRE = 2      # Pantalla 2: Donde escribes tu nombre.
ESTADO_ERROR_FATAL = 3 # Pantalla 3: Pantalla de error si algo sale muy mal.
ESTADO_VICTORIA = 4    # Pantalla 4: Pantalla de celebración final.

# =====================================================================
# 4. FABRICANDO LAS PIEZAS DEL JUEGO (Clases / Moldes)
# =====================================================================
# Creamos el "molde" para construir nuestro Dado.
class Dado:
    def tirar(self):
        # Esta acción simplemente escoge un número al azar del 1 al 6 y lo entrega.
        return random.randint(1,6)
    
# Usamos el molde para fabricar un dado real que usaremos luego.
dado = Dado()

# Creamos el "molde" para construir las fichas de los jugadores.
class Ficha:
    # Esta es la acción que se ejecuta automáticamente al "nacer" una ficha nueva.
    def __init__(self, ID, image_path):
        self.ID = ID             # Le ponemos una etiqueta (Jugador 0, Jugador 1...).
        self.casilla_actual = 0  # Decimos que su posición inicial es fuera del tablero (casilla 0).
        self.radio = 25          # Su tamaño redondo imaginario para saber dónde hacer clic.
        self.texture = None      # Preparamos una caja vacía para guardar su dibujo.
        # Intentamos hacer algo que puede fallar (cargar la imagen del disco duro).
        try:
            # Metemos la imagen en la tarjeta gráfica para que se pueda dibujar en pantalla.
            self.texture = arcade.load_texture(image_path)
        # Si la imagen no está en la carpeta, no rompemos el juego, solo avisamos del error.
        except Exception as e:
            print(f"Error carga imagen {ID}: {e}")

# =====================================================================
# 5. EL JUEGO EN SÍ MISMO (La Ventana Principal)
# =====================================================================
# Creamos la caja principal del juego que hereda el poder de ser una Ventana en el ordenador.
class OcaGame(arcade.Window):
    
    # -----------------------------------------------------------------
    # PREPARATIVOS ANTES DE JUGAR (Como sacar la caja a la mesa)
    # -----------------------------------------------------------------
    def __init__(self):
        # Le pedimos a Windows (o Mac) que nos abra una ventana a pantalla completa con nuestro título.
        super().__init__(title=SCREEN_TITLE, fullscreen=True)
        
        # Hacemos que la flechita del ratón se vea en la pantalla.
        self.set_mouse_visible(True)        
        self.estado = ESTADO_MENU           # Le decimos que empiece enseñando el Menú Principal (0).
        self.jugador_elegido = None         # Todavía no sabemos qué ficha va a elegir el jugador.
        self.nombre = ""                    # Dejamos un texto en blanco preparado para guardar su nombre.
        self.tiempo_error = 0.0             # Un reloj a cero por si hay un error y tenemos que cerrar.
        self.contador_tiradas = 0           # Un contador a cero para ver cuántas veces tira el dado.
        self.animacion_victoria = 0.0       # Un reloj a cero para animar las letras al ganar.
        
        self.background = None              # Caja vacía para el dibujo del fondo.
        self.usar_imagen_fondo = False      # Un interruptor apagado: por ahora no hay fondo.
        self.textura_casilla_1 = None       # Caja vacía para el dibujo de la Salida.

        # Cargamos en la tarjeta gráfica el dibujo del botón de Start y de Fin.
        self.textura_casilla_1 = arcade.load_texture("assets/img/icons/BotonStart.png")
        self.textura_casilla_36 = arcade.load_texture("assets/img/icons/BotonFin.png")

        print("Cargando recursos... ⚙️")   # Un mensaje para nosotros en la consola de comandos.
        
        # Buscamos dónde está el archivo del fondo.
        ruta_fondo = os.path.join("assets", "img", "fondo", "FondoNuevo.jpg")
        # Intentamos cargar ese fondo.
        try:
            self.background = arcade.load_texture(ruta_fondo) # Guardamos la imagen en memoria.
            self.usar_imagen_fondo = True                     # Encendemos el interruptor de fondo.
        # Si el fondo se borró por error, pintamos el fondo de gris para que no explote nada.
        except Exception as e:
            print(f"Error cargando la imagen de fondo: {e}")
            self.background_color = arcade.color.GRAY 

        # Preparamos una lista vacía para guardar las 6 caras del dado.
        self.texturas_dado = []
        # Repetimos esta acción 6 veces (del 1 al 6).
        for i in range(1, 7):
            # Buscamos el nombre del archivo (cara1.png, cara2.png...).
            ruta_dado = f"assets/img/Dados/cara{i}.png"
            # Intentamos guardar esa cara del dado en nuestra lista.
            try:
                textura = arcade.load_texture(ruta_dado)
                self.texturas_dado.append(textura)
            # Si falta una imagen, lo ignoramos y seguimos cargando las demás.
            except Exception as e:
                print(f"Error cargando imagen del dado {i}: {e}")

        self.camino = []         # Lista vacía donde apuntaremos dónde va cada casilla.
        self.generar_espiral()   # Llamamos a una orden matemática (más abajo) para que llene esa lista.
        
        # Fabricamos 4 fichas de golpe usando el molde que creamos antes y las guardamos en una lista.
        self.jugadores = [Ficha(i, PLAYER_IMAGES[i]) for i in range(4)]
        self.turno_actual = 0    # Apuntamos que le toca al primer jugador (que en programación es el 0).
        
        # Listas con los números de las casillas que tienen castigos o premios.
        self.casillas_penalizacion = [9, 18, 26] 
        self.casillas_turbo = [5, 14, 22]        

        # Interruptores y datos en blanco para cuando salten las preguntas.
        self.mostrando_pregunta = False  # Ahora mismo no hay preguntas en pantalla.
        self.pregunta_actual = None      # Caja vacía para la pregunta que salga.
        self.botones_rects = []          # Lista vacía para saber dónde estarán los botones para hacer clic.
        self.resultado_quiz = None       # Caja vacía para guardar si acertó o falló.
        self.tiempo_feedback = 0         # Reloj a cero para borrar el mensaje de "Acertaste".
        self.lista_preguntas = []        # Lista vacía donde meteremos todas las preguntas.
        
        # Llamamos a la orden que abre el archivo de texto y lee las preguntas.
        self.cargar_preguntas_json() 
        
        # Interruptores para la ruleta que anima el dado al tirar.
        self.dado_animacion_activa = False # El dado no se está moviendo.
        self.dado_timer = 0.0              # Reloj a cero para la animación.
        self.dado_valor_final = 1          # El número final que tocará.
        self.dado_tiradas = 0              # Cuántas veces hemos pulsado para tirar.

    # -----------------------------------------------------------------
    # ACCIONES SECRETAS (Lectura de archivos y descargas)
    # -----------------------------------------------------------------
    def cargar_textura_ninja(self, url, nombre_temp, es_fondo):
        # Esta acción es un truco: intenta descargar una foto de internet, usarla y luego borrar el rastro.
        try:
            # Pide la foto a internet haciéndose pasar por un navegador normal.
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # Guarda el archivo descargado en tu ordenador.
            with urllib.request.urlopen(req) as response, open(nombre_temp, 'wb') as out_file:
                out_file.write(response.read())
            # Lo carga en el juego.
            textura = arcade.load_texture(nombre_temp)
            if es_fondo:
                self.background = textura
                self.usar_imagen_fondo = True
            else:
                self.textura_casilla_1 = textura
            # Destruye la prueba borrando la imagen descargada.
            if os.path.exists(nombre_temp): os.remove(nombre_temp)
        except Exception:
            # Si no hay internet, al menos pon un fondo gris.
            if es_fondo: self.background_color = arcade.color.GRAY

    def cargar_preguntas_json(self):
        # Esta acción saca las preguntas del archivo de texto.
        self.lista_preguntas = []
        ruta_json = os.path.join("assets", "preguntas.json")

        # Comprueba: "¿Existe este archivo en el ordenador?". Si no, rompe el juego con un Error Fatal.
        if not os.path.exists(ruta_json):
            self.estado = ESTADO_ERROR_FATAL 
            return # Se detiene aquí, no sigue leyendo.

        try:
            # Abre el archivo como si fuera un libro, preparado para leer tildes y ñ (utf-8).
            with open(ruta_json, "r", encoding="utf-8") as archivo:
                # Transforma ese texto crudo en bloques de información ordenados.
                datos = json.load(archivo)
                # Extrae de esos bloques la lista de "preguntas".
                self.lista_preguntas = datos.get("preguntas", [])
                
            # Si el archivo estaba vacío... Error Fatal.
            if len(self.lista_preguntas) == 0:
                self.estado = ESTADO_ERROR_FATAL 
            else:
                # Nos avisa de que todo fue bien.
                print(f"[OK] Se han cargado {len(self.lista_preguntas)} categorías de preguntas.")

        except Exception as e:
            # Si algo falló al leer el texto (estaba mal escrito), salta un error y bloquea el juego.
            print(f"[ERROR] Fallo al leer el JSON: {e}. Activando Modo Oca Clásica.")
            self.estado = ESTADO_ERROR_FATAL 

    def cargar_ranking(self):
        # Acción para leer la lista de ganadores.
        ruta_ranking = os.path.join("assets", "ranking.json")
        # Si nadie ha jugado nunca (no existe el archivo), devuelve una lista vacía.
        if not os.path.exists(ruta_ranking):
            return []
            
        try:
            # Si existe, lo abre y devuelve la lista de ganadores.
            with open(ruta_ranking, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except Exception:
            return [] # Si falla, también devuelve una lista vacía.
        
    def guardar_puntuacion(self, nombre, categoria, tiradas):
        # Acción para anotar un nuevo ganador en el archivo.
        ranking = self.cargar_ranking() # Coge la lista de ganadores antiguos.
        
        # Creamos una cajita (diccionario) con los datos del nuevo ganador.
        nuevo_record = {
            "nombre": nombre,
            "categoria": categoria,
            "tiradas": tiradas,
            "fecha": str(datetime.date.today()) # Mira qué día es hoy en el ordenador.
        }
        # Añade la nueva cajita a la lista de ganadores.
        ranking.append(nuevo_record)
        
        ruta_ranking = os.path.join("assets", "ranking.json")
        try:
            # Abre el archivo en modo escritura ("w") para sobrescribirlo entero.
            with open(ruta_ranking, "w", encoding="utf-8") as archivo:
                # Escribe la lista actualizada en el archivo para que se guarde de verdad.
                json.dump(ranking, archivo, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar puntuación: {e}")

    def obtener_top_10(self):
        # Acción para sacar solo a los 10 mejores jugadores.
        ranking = self.cargar_ranking()
        # Ordena la lista fijándose solamente en quién usó menos "tiradas" de dado.
        ranking.sort(key=lambda x: x['tiradas'])
        # Recorta la lista y nos da solo los de la posición 0 a la 9 (los 10 primeros).
        return ranking[:10]

    # -----------------------------------------------------------------
    # MATEMÁTICAS (Cálculo de posiciones en la pantalla)
    # -----------------------------------------------------------------
    def generar_espiral(self):
        # Esta acción hace los cálculos para dibujar el caminito de casillas haciendo círculos.
        total_casillas = 36
        # Definimos los bordes del tablero cuadrado (columna 0 a la 5, fila 0 a la 5).
        col_inicio, col_fin, fila_inicio, fila_fin = 0, 5, 0, 5
        n = 1 # Empezamos por la casilla número 1.
        
        # Repetimos mientras no hayamos llegado a la casilla 36.
        while n <= total_casillas:
            # Trazamos línea hacia la derecha.
            for i in range(col_inicio, col_fin + 1):
                if n > total_casillas: break
                self.camino.append((i, fila_inicio, n)); n += 1
            fila_inicio += 1
            
            # Trazamos línea hacia abajo.
            for i in range(fila_inicio, fila_fin + 1):
                if n > total_casillas: break
                self.camino.append((col_fin, i, n)); n += 1
            col_fin -= 1
            
            # Trazamos línea hacia la izquierda.
            for i in range(col_fin, col_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((i, fila_fin, n)); n += 1
            fila_fin -= 1
            
            # Trazamos línea hacia arriba.
            for i in range(fila_fin, fila_inicio - 1, -1):
                if n > total_casillas: break
                self.camino.append((col_inicio, i, n)); n += 1
            col_inicio += 1

    def obtener_offsets(self):
        # Esta acción calcula el centro exacto de TU monitor (ya que cada uno tiene un monitor distinto).
        tablero_ancho = 6 * (CELL_SIZE + MARGIN)
        tablero_alto = 6 * (CELL_SIZE + MARGIN)
        # Calcula cuánto sobra de pantalla a los lados y lo parte por la mitad.
        off_x = (self.width - tablero_ancho) // 2
        off_y = (self.height // 2) + (tablero_alto // 2) - CELL_SIZE - 110
        return off_x, off_y

    def obtener_coordenadas_casilla(self, numero_casilla):
        # Esta acción averigua dónde está exactamente una casilla concreta (para mover la ficha allí).
        if numero_casilla == 0:
            off_x, _ = self.obtener_offsets()
            return off_x - 100, self.height // 2 # Si es la 0, ponla fuera del tablero a la izquierda.
            
        off_x, off_y = self.obtener_offsets()
        # Busca en nuestro camino imaginario dónde encaja la casilla y nos da su posición real (x, y).
        for col, fila, num in self.camino:
            if num == numero_casilla:
                x = off_x + col * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                y = off_y - fila * (CELL_SIZE + MARGIN) + CELL_SIZE / 2
                return x, y
        return 0, 0 # Si no la encuentra, devuelve 0,0 por seguridad.

    def activar_pregunta(self):
        # Esta acción saca la tarjeta de preguntas en la pantalla.
        self.mostrando_pregunta = True  # Enciende la señal para que se dibuje la pregunta.
        self.resultado_quiz = None      # Borra cualquier acierto o fallo anterior.
        
        # Una lista con los nombres exactos de las profesiones.
        categorias = ["Obra", "Imagen personal", "Informática", "Madera"]
        # Averigua a qué profesión pertenece la ficha con la que estás jugando.
        categoria_elegida = categorias[self.jugador_elegido]

        preguntas_de_esta_categoria = []
        # Rebusca en la gran lista de preguntas.
        for bloque in self.lista_preguntas:
            # Si el bloque es correcto y la profesión coincide, saca esas preguntas.
            if isinstance(bloque, dict) and bloque.get("categoria", "").lower() == categoria_elegida.lower():
                preguntas_de_esta_categoria = bloque.get("items", [])
                break # Deja de buscar.
        
        # Si encontró preguntas...
        if preguntas_de_esta_categoria:
            # Escoge una completamente al azar.
            self.pregunta_actual = random.choice(preguntas_de_esta_categoria)
        # Si hubo un error y no hay preguntas...
        else:
            # Crea una pregunta falsa de error para que el juego no estalle.
            self.pregunta_actual = {
                "pregunta": f"Error: No se encontraron preguntas para {categoria_elegida}", 
                "opciones": ["A", "B", "C", "D"], 
                "correcta": "A"
            }
        
        # Ahora va a calcular en qué partes de la pantalla pondrá los 4 botones de respuesta (cajas imaginarias).
        self.botones_rects = []
        cx = self.width // 2 # Centro horizontal de la pantalla.
        cy = self.height // 2 # Centro vertical.
        ancho_btn, alto_btn = 500, 60 # Tamaño de cada botón.
        start_y = cy - 20
        
        # Repite esto 4 veces (para las 4 opciones A, B, C, D).
        for i in range(4):
            y = start_y - (i * 80) # Va bajando el botón un poco más cada vez.
            x = cx - (ancho_btn // 2) # Centra el botón horizontalmente.
            # Guarda la posición y tamaño exacto del botón en la lista.
            self.botones_rects.append((x, y, ancho_btn, alto_btn))

    # -----------------------------------------------------------------
    # EL VIGILANTE (Acciones cuando tocas el ratón o el teclado)
    # -----------------------------------------------------------------
    def on_mouse_press(self, x, y, button, modifiers):
        # El ordenador detecta que has hecho "clic" mágico y nos dice en qué coordenadas (x, y) de la pantalla.
        
        # Si estamos en pantalla de error fatal, ignoramos tus clics por completo.
        if self.estado == ESTADO_ERROR_FATAL:
            return

        # Si estamos en el Menú Inicial...
        if self.estado == ESTADO_MENU:
            # Revisa las 4 imágenes de las fichas en la pantalla.
            for i in range(4):
                cx = self.width // 2 - 300 + (i * 200) # Calcula dónde está el centro de esa ficha.
                cy = self.height // 2
                # Fórmula matemática para medir a qué distancia has hecho el clic del centro de la ficha.
                distancia = math.sqrt((x - cx)**2 + (y - cy)**2) 
                # Si has hecho clic a menos de 80 pasos de distancia del centro (es decir, encima del dibujo).
                if distancia < 80:
                    self.jugador_elegido = i # Apuntamos qué ficha elegiste.
                    self.turno_actual = i              
                    self.estado = ESTADO_NOMBRE # Cambiamos de pantalla: ¡A pedir el nombre!
                    print(f"Elegido: {i}. Pasando a pedir nombre...")
        
        # Si estamos jugando Y hay una pregunta en pantalla...
        elif self.estado == ESTADO_JUEGO and self.mostrando_pregunta:
            # Si todavía no has respondido a esta pregunta...
            if self.resultado_quiz is None:
                # Diccionario para traducir letras (A,B,C,D) a números (0,1,2,3).
                mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
                # Averiguamos qué botón (0,1,2 o 3) es el que tiene la respuesta correcta.
                idx_correcto = mapa_letras.get(self.pregunta_actual["correcta"], 0)

                # Comprobamos los 4 rectángulos que dibujamos antes para las respuestas.
                for i, rect in enumerate(self.botones_rects):
                    # Extraemos izquierda, abajo, ancho y alto de ese botón.
                    bx, by, bw, bh = rect
                    # Si tu clic cayó DENTRO de esos bordes...
                    if bx < x < bx + bw and by < y < by + bh:
                        # Si encima resulta que ese era el botón correcto...
                        if i == idx_correcto:
                            self.resultado_quiz = "CORRECTO" # Marcamos acierto.
                            self.contador_tiradas += 1       # Apuntamos que gastaste un turno.
                            
                            jugador = self.jugadores[self.jugador_elegido] # Miramos a tu jugador.
                            
                            # Si sumándole lo que sacó el dado ya se pasa de la meta (36)...
                            if jugador.casilla_actual + self.dado_valor_final >= 36:
                                jugador.casilla_actual = 36 # Lo dejamos en la 36 (Meta).
                                categorias = ["Obra", "Imagen personal", "Informática", "Madera"]
                                # Guardamos tu partida en el archivo de texto.
                                self.guardar_puntuacion(self.nombre, categorias[self.jugador_elegido], self.contador_tiradas)
                                self.estado = ESTADO_VICTORIA # Cambiamos a la pantalla final.
                            # Si no ha llegado a la meta, simplemente se mueve.
                            else:
                                jugador.casilla_actual += self.dado_valor_final

                            # Si cayó en casilla de castigo, retrocede 3, pero asegurándonos de no salirse del tablero (mínimo 1).
                            if jugador.casilla_actual in self.casillas_penalizacion:
                                jugador.casilla_actual = max(1, jugador.casilla_actual - 3)
                            # Si cayó en turbo, avanza 5, asegurándonos de no pasarse de la meta (máximo 36).
                            if jugador.casilla_actual in self.casillas_turbo:
                                jugador.casilla_actual = min(36, jugador.casilla_actual + 5)
                        # Si hiciste clic en el botón equivocado...
                        else:
                            self.resultado_quiz = "INCORRECTO" # Marcamos fallo y te quedas sin mover.
                        return 
            # Si ya se mostró si acertaste o fallaste, un simple clic cierra la ventana de pregunta.
            else:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0 
                self.resultado_quiz = None

    def on_text(self, text):
        # El ordenador detecta que has tecleado una letra física.
        if self.estado == ESTADO_ERROR_FATAL:
            return

        # Si estamos en la pantalla de escribir tu nombre...
        if self.estado == ESTADO_NOMBRE:
            # Si tu nombre tiene menos de 15 letras (para que no se salga de la pantalla)...
            if len(self.nombre) < 15: 
                # Si es una letra normal (no el botón Ctrl o Enter)...
                if text.isprintable() and text != '\r':
                    self.nombre += text # Añade esa letra a tu nombre.

    def on_key_press(self, key, modifiers):
        # El ordenador detecta si aprietas teclas de control especial (Enter, Espacio, Escape...).
        if self.estado == ESTADO_ERROR_FATAL:
            return

        # Si estás en la pantalla de pedir nombre...
        if self.estado == ESTADO_NOMBRE:
            # Si pulsas ENTER, comprueba si has escrito algo, si no pone "Jugador 1" y empieza el juego.
            if key == arcade.key.ENTER:
                if self.nombre.strip() == "":
                    self.nombre = "Jugador 1"
                self.estado = ESTADO_JUEGO
            # Si pulsas BORRAR (Retroceso), elimina la última letra que escribiste.
            elif key == arcade.key.BACKSPACE:
                self.nombre = self.nombre[:-1]
            return 
        
        # Si en cualquier momento pulsas la tecla ESCAPE, cierra la ventana entera.
        if key == arcade.key.ESCAPE:
            self.close()
        # Si pulsas F11, cambia entre pantalla completa o ventana chiquita.
        elif key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)
            self.set_mouse_visible(True)
            
        # Si estás en el Tablero Y pulsas la barra ESPACIADORA...
        if self.estado == ESTADO_JUEGO and key == arcade.key.SPACE:
            # Si no hay ninguna pregunta tapando la pantalla... ¡A tirar el dado!
            if not self.mostrando_pregunta:
                self.dado_tiradas +=1              # Sube el contador total de tiradas.
                pasos = dado.tirar()               # Lanza el dado matemático.
                self.dado_animacion_activa = True  # Arranca la animación visual del dado.
                self.dado_timer = 5.5              # Ponemos el reloj a contar 5.5 segundos.
                self.dado_valor_final = pasos      # Guardamos el número que salió.
                
                # Si aún no has llegado a la meta y el archivo de preguntas funciona...
                if self.jugadores[self.jugador_elegido].casilla_actual < 36:
                    if len(self.lista_preguntas) > 0:
                        self.activar_pregunta()    # Saca una pregunta a pantalla.
                    
            # Si pulsaste Espacio pero era porque estabas viendo si habías acertado o no, ciérralo.
            elif self.mostrando_pregunta and self.resultado_quiz is not None:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0
                self.resultado_quiz = None

            # Si estás en la pantalla de que ya ganaste, pulsar ENTER reinicia todo el juego.
            if self.estado == ESTADO_VICTORIA and key == arcade.key.ENTER:
                self.estado = ESTADO_MENU
                self.contador_tiradas = 0
                for j in self.jugadores: 
                    j.casilla_actual = 0

    # -----------------------------------------------------------------
    # EL RELOJ INTERNO (Actualizar temporizadores)
    # -----------------------------------------------------------------
    def on_update(self, delta_time):
        # Esta acción se dispara unas 60 veces por segundo automáticamente para llevar la cuenta del tiempo.
        # "delta_time" es la fracción de segundo (0.016s) que pasó desde la última vez que preguntó.
        
        # Si hay un error, el reloj suma tiempo hasta llegar a 10 segundos y luego nos echa.
        if self.estado == ESTADO_ERROR_FATAL:
            self.tiempo_error += delta_time
            if self.tiempo_error >= 10.0:
                self.close()  
            return 

        # Si hay un resultado de Correcto/Incorrecto en pantalla...
        if self.resultado_quiz is not None:
            self.tiempo_feedback += delta_time
            # Si ya pasaron 2 segundos viéndolo, ciérralo para que la ficha se mueva.
            if self.tiempo_feedback > 2.0:
                self.mostrando_pregunta = False
                self.tiempo_feedback = 0
                self.resultado_quiz = None

        # Si el dado está haciendo su efecto visual de dar vueltas...
        if getattr(self, "dado_animacion_activa", False):
            self.dado_timer -= delta_time # Va restando tiempo de la cuenta atrás de 5.5 segundos.
        # Si el reloj del dado llegó a cero, apaga el efecto visual del dado.
        if self.dado_timer <= 0:
                self.dado_animacion_activa = False

        # Si estás en la victoria, este reloj ayuda a animar el latido del texto más grande y pequeño.
        if self.estado == ESTADO_VICTORIA:
            self.animacion_victoria += delta_time

    # -----------------------------------------------------------------
    # EL PINTOR (Acciones puramente visuales, dibujar la pantalla)
    # -----------------------------------------------------------------
    def on_draw(self):
        # Esta acción es el "pintor". Se activa unas 60 veces por segundo para colorear la pantalla de tu ordenador.
        
        # Lo primero que hace el pintor es borrar el lienzo con una goma gigante para evitar manchones.
        self.clear()
        
        # Si hay una imagen de fondo, pégala gigante cubriendo toda la pantalla.
        if self.usar_imagen_fondo and self.background:
            arcade.draw_texture_rect(self.background, arcade.XYWH(self.width / 2, self.height / 2, self.width, self.height))

        # Dependiendo del número de pantalla (estado), llama a un ayudante distinto del pintor para dibujar la escena.
        if self.estado == ESTADO_ERROR_FATAL:
            self.dibujar_error_fatal()
        elif self.estado == ESTADO_MENU:
            self.dibujar_menu()            
        elif self.estado == ESTADO_NOMBRE:
            self.dibujar_ingreso_nombre()
        elif self.estado == ESTADO_JUEGO:
            self.dibujar_tablero_y_fichas()
        elif self.estado == ESTADO_VICTORIA:
            self.dibujar_victoria()
        
        # Si el interruptor de preguntar está encendido, dibuja la tarjeta de pregunta POR ENCIMA de lo anterior.
        if self.mostrando_pregunta and self.pregunta_actual:
            self.dibujar_capa_pregunta()
            
        # Si la animación del dado está encendida, dibuja el dado dando vueltas por encima de todo.
        if getattr(self, "dado_animacion_activa", False):
            cx = self.width // 6  # Lo pone un poco hacia la izquierda.
            cy = self.height // 2 # Centrado verticalmente.
            
            # Dibuja un cuadrado semitransparente como base.
            arcade.draw_rect_filled(arcade.XYWH(cx, cy, 250, 250), (0, 0, 0, 220))
            arcade.draw_rect_outline(arcade.XYWH(cx, cy, 250, 250), arcade.color.WHITE, 5) # Borde blanco.
            
            # Si estamos en los primeros segundos de animación, simula que gira pintando caras al azar.
            if self.dado_timer > 4.0:
                valor_mostrar = random.randint(1, 6)
                texto_dado = "TIRANDO..."
                color_texto = arcade.color.WHITE
            # Cuando falte poco para el final, frena el dado y muestra el número real que tocó.
            else:
                valor_mostrar = self.dado_valor_final
                texto_dado = "¡RESULTADO!"
                color_texto = arcade.color.GOLD
                
            # Si se cargaron las fotos del dado correctamente, dibuja la foto correspondiente.
            if len(self.texturas_dado) == 6:
                textura_actual = self.texturas_dado[valor_mostrar - 1] # -1 porque las listas en Python empiezan en 0.
                arcade.draw_texture_rect(textura_actual, arcade.XYWH(cx, cy, 150, 150))
            # Si no hay fotos, simplemente escribe el número grandote.
            else:
                arcade.draw_text(str(valor_mostrar), cx, cy - 20, color_texto, 
                                        120, anchor_x="center", anchor_y="center", bold=True)
            
            # Escribe la palabra "TIRANDO" o "RESULTADO".
            arcade.draw_text(texto_dado, cx, cy - 160, arcade.color.WHITE, 
                                    24, anchor_x="center", anchor_y="center", bold=True)

    # Las siguientes son las "órdenes de pintura" de cada escena específica. Son puramente visuales.

    def dibujar_error_fatal(self):
        # Pinta la pantalla toda de negro.
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), arcade.color.BLACK)
        # Escribe mensajes de error en rojo y blanco en el centro de la pantalla.
        arcade.draw_text("⚠️ ERROR ⚠️", self.width // 2, self.height // 2 + 100,
                         arcade.color.RED, 50, anchor_x="center", bold=True)
        arcade.draw_text("Avisar al profesor que falta el archivo de preguntas", self.width // 2, self.height // 2,
                         arcade.color.WHITE, 30, anchor_x="center", bold=True)
        # Calcula cuánto falta para 10 segundos y lo escribe en gris.
        segundos_restantes = max(0, 10 - int(self.tiempo_error))
        arcade.draw_text(f"El juego se cerrará automáticamente en {segundos_restantes}...", self.width // 2, self.height // 2 - 100,
                         arcade.color.GRAY, 20, anchor_x="center")

    def dibujar_menu(self):                
        # Dibuja un cuadrado negro semitransparente como velo oscuro (como ponerle gafas de sol a la pantalla).
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 150))
        arcade.draw_text("SELECCIONA TU CATEGORÍA", self.width // 2, self.height // 2 + 200,
                         arcade.color.WHITE, 45, anchor_x="center", bold=True)
        
        nombres = ["OBRA", "IMAGEN PERSONAL", "INFORMÁTICA", "MADERA"]
        # Repite esto para colocar 4 imágenes separadas en fila.
        for i in range(4):
            cx = self.width // 2 - 300 + (i * 200) # Calcula su sitio horizontal.
            cy = self.height // 2
            # Si la foto de la ficha se cargó con éxito, píntala ahí.
            if self.jugadores[i].texture:
                arcade.draw_texture_rect(self.jugadores[i].texture, arcade.XYWH(cx, cy, 120, 120))
            # Dibuja el nombre de la profesión debajo de su foto.
            arcade.draw_text(nombres[i], cx, cy - 100, arcade.color.WHITE, 18, anchor_x="center", bold=True)

    def dibujar_ingreso_nombre(self):
        # Pantalla con velo oscuro.
        arcade.draw_rect_filled(arcade.LBWH(0, 0, self.width, self.height), (0, 0, 0, 180))
        arcade.draw_text("INTRODUCE TU NOMBRE:", self.width // 2, self.height // 2 + 50,
                         arcade.color.WHITE, 35, anchor_x="center", bold=True)
        
        # Escribe las letras que vayas tecleando más un "_" al final para que parezca que estás escribiendo.
        arcade.draw_text(self.nombre + "_", self.width // 2, self.height // 2 - 20,
                         arcade.color.GOLD, 45, anchor_x="center", bold=True)
        
        arcade.draw_text("Pulsa ENTER para comenzar", self.width // 2, self.height // 2 - 100,
                         arcade.color.GRAY, 20, anchor_x="center")

    def dibujar_tablero_y_fichas(self):
        off_x, off_y = self.obtener_offsets() # Pide el centro exacto de la pantalla.
        
        # Pinta cada casilla de la espiral una a una.
        for col, fila, num in self.camino:
            x, y = off_x + col * (CELL_SIZE + MARGIN), off_y - fila * (CELL_SIZE + MARGIN) # Posición X e Y.
            rect_casilla = arcade.LBWH(x, y, CELL_SIZE, CELL_SIZE) # Molde del cuadrado.
            
            # Si es la salida (1), pon su foto especial.
            if num == 1 and self.textura_casilla_1:
                arcade.draw_texture_rect(self.textura_casilla_1, rect_casilla)
            # Si es la meta (36), pon su foto especial.
            elif num == 36 and self.textura_casilla_36:
                arcade.draw_texture_rect(self.textura_casilla_36, rect_casilla)
            # Si es cualquier otra...
            else:
                # Decide qué color toca según si es mala, buena o neutra.
                if num in self.casillas_penalizacion:
                    color_fondo = arcade.color.RED     # Rojo malo.
                elif num in self.casillas_turbo:
                    color_fondo = arcade.color.BLUE    # Azul bueno.
                elif num == 36:
                    color_fondo = arcade.color.ORANGE  # Naranja meta (por si falló la imagen).
                else:
                    color_fondo = arcade.color.GREEN   # Verde normal.
                # Pinta el interior de la casilla con ese color.
                arcade.draw_rect_filled(rect_casilla, color_fondo)
                
            # Pinta el marco negro alrededor.
            arcade.draw_rect_outline(rect_casilla, arcade.color.BLACK, 2)
            # Dibuja el número dentro (salvo en salida y meta).
            if num not in (1, 36):
                arcade.draw_text(str(num), x + CELL_SIZE/2, y + CELL_SIZE/2, arcade.color.BLACK, 24, anchor_x="center", bold=True)

        # Ahora pinta a los jugadores.
        for i, jugador in enumerate(self.jugadores):
            # Solo dibuja al jugador activo actual (la idea original quizá era multijugador, pero aquí solo dibujamos al tuyo).
            if i == self.jugador_elegido: 
                posX, posY = self.obtener_coordenadas_casilla(jugador.casilla_actual) # Pide dónde toca pintarlo.
                dx, dy = 0, 0 
                # Si tiene foto, plántala ahí en chiquito.
                if jugador.texture:
                    arcade.draw_texture_rect(jugador.texture, arcade.XYWH(posX + dx, posY + dy, 60, 60))
                
                # Ponle la palabra "TÚ" debajo para que sepas dónde andas.
                arcade.draw_text("TÚ", posX + dx, posY + dy + 45, arcade.color.WHITE, 14, anchor_x="center", bold=True)

        # Letreros informativos por arriba y por abajo en la pantalla.
        nombres = ["OBRA", "IMAGEN PERSONAL", "INFORMÁTICA", "MADERA"]
        texto = f"Familia profesional: {nombres[self.jugador_elegido].capitalize()} - Pulsa ESPACIO para tirar el dado" 
        arcade.draw_text(texto, self.width // 2, 20, arcade.color.WHITE, 24, anchor_x="center", bold=True)

        arcade.draw_text(f"Jugador: {self.nombre}", 20, self.height - 40, 
                         arcade.color.WHITE, 22, bold=True)
        
        arcade.draw_text(f"TIRADAS: {self.dado_tiradas}", 20, self.height - 80, arcade.color.GOLD, 22, bold=True)

    def dibujar_capa_pregunta(self):
        # Pinta un velo súper oscuro (230 de 255) para tapar el tablero y que nos centremos en la pregunta.
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 230))
        cx = self.width // 2
        cy = self.height // 2

        # Dibuja el texto de la pregunta, permitiendo saltos de línea si es muy larga.
        arcade.draw_text(
            self.pregunta_actual["pregunta"], cx, cy + 150, arcade.color.WHITE,
            30, anchor_x="center", anchor_y="center", width=900, align="center", multiline=True, bold=True
        )

        letras = ["A", "B", "C", "D"] # Para que salgan los incisos.
        colores_base = [arcade.color.BLUE, arcade.color.RED, arcade.color.AMBER, arcade.color.GREEN] # Colores chulos de los botones.
        mapa_letras = {"A": 0, "B": 1, "C": 2, "D": 3}
        idx_correcto = mapa_letras.get(self.pregunta_actual["correcta"], 0) # Saber cuál es la letra ganadora.

        # Pinta los 4 botones.
        for i, rect in enumerate(self.botones_rects):
            x, y, w, h = rect
            color_btn = colores_base[i]
            
            # Si acabas de responder... ilumina la correcta de oro y apaga las demás en gris oscuro.
            if self.resultado_quiz is not None:
                if i == idx_correcto:
                    color_btn = arcade.color.GOLD  
                else:
                    color_btn = arcade.color.GRAY  
            
            # Dibuja el fondo y el borde blanco del botón.
            arcade.draw_lbwh_rectangle_filled(x, y, w, h, color_btn)
            arcade.draw_lbwh_rectangle_outline(x, y, w, h, arcade.color.WHITE, 3)
            
            # Si el fondo del botón es claro, las letras serán negras para que se lea. Si es oscuro, letras blancas.
            if color_btn in (arcade.color.GOLD, arcade.color.AMBER, arcade.color.GREEN, arcade.color.YELLOW):
                color_texto = arcade.color.BLACK
            else:
                color_texto = arcade.color.WHITE

            # Pega el texto de la respuesta (A, B, C o D) dentro de su botón correspondiente.
            texto_op = f"{letras[i]}) {self.pregunta_actual['opciones'][i]}"
            arcade.draw_text(texto_op, x + w / 2, y + h / 2, color_texto, 18, anchor_x="center", anchor_y="center")

        # Si ya has respondido, saca un letrero grandote diciendo si acertaste o no.
        if self.resultado_quiz:
            texto_res = "¡CORRECTO!" if self.resultado_quiz == "CORRECTO" else "¡FALLASTE!"
            color_res = arcade.color.GREEN if self.resultado_quiz == "CORRECTO" else arcade.color.RED
            
            arcade.draw_text(texto_res, cx, cy + 300, color_res, 40, anchor_x="center", bold=True)

    
    def dibujar_victoria(self):
        # Velo súper oscuro.
        arcade.draw_lbwh_rectangle_filled(0, 0, self.width, self.height, (0, 0, 0, 230))
        # Hace que la letra cambie de tamaño simulando que "late" como un corazón, usando la función matemática "Seno".
        escala = 50 + math.sin(self.animacion_victoria) * 5
        arcade.draw_text("🎉 ¡HAS GANADO! 🎉", self.width // 2, self.height - 150, arcade.color.GOLD, escala, anchor_x="center", bold=True)
        arcade.draw_text(f"{self.nombre} terminó en {self.contador_tiradas} tiradas", self.width // 2, self.height - 230, arcade.color.WHITE, 24, anchor_x="center")
        
        # Pinta la lista de los 10 mejores campeones de la historia.
        arcade.draw_text("🏆 TOP 10 JUGADORES 🏆", self.width // 2, self.height - 320, arcade.color.WHITE, 35, anchor_x="center")
        top10 = self.obtener_top_10() # Recupera a los ganadores de la memoria.
        y = self.height - 380
        medallas = ["🥇", "🥈", "🥉"] # Emoticonos chulos para los 3 primeros.
        for i, jugador in enumerate(top10):
            # Si estás entre los 3 primeros te pone medalla, si no, solo tu número de posición (4., 5., 6...).
            prefijo = medallas[i] if i < 3 else f"{i+1}."
            texto = f"{prefijo} {jugador['nombre']} - {jugador['tiradas']} tiradas"
            arcade.draw_text(texto, self.width // 2, y, arcade.color.WHITE, 22, anchor_x="center")
            y -= 35 # Va bajando el lápiz como si saltara de renglón en un cuaderno.
        arcade.draw_text("Pulsa ENTER para volver al menú", self.width // 2, 100, arcade.color.GRAY, 20, anchor_x="center")

# =====================================================================
# 6. EL BOTÓN DE ENCENDIDO
# =====================================================================
# Esta es la acción que hace de "chispazo" inicial para arrancar toda la maquinaria del juego que programamos arriba.
def main():
    OcaGame()     # Saca la caja fuerte de nuestro juego (la crea).
    arcade.run()  # Gira la llave: enciende el motor de PyArcade para que nunca se cierre sola.

# Esto es un pestillo de seguridad típico de Python. 
# Dice: "Solo dale al botón de encendido si alguien hizo doble clic directamente en mí".
if __name__ == "__main__":
    main()