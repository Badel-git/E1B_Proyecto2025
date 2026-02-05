import arcade
import json
import random

W, H = 420, 300   # ← ventana más pequeña


class VentanaPregunta(arcade.Window):

    def __init__(self, datos):
        super().__init__(W, H, "Pregunta")

        arcade.set_background_color(arcade.color.WHITE)

        self.p = datos["pregunta"]
        self.ops = datos["opciones"]
        self.ok = datos["correcta"]

        self.res = None
        self.botones = [
            arcade.LBWH(40, 150 - i*45, 340, 35)
            for i in range(4)
        ]

    def on_draw(self):
        self.clear()

        arcade.draw_text(self.p, W//2, 260,
                         arcade.color.BLACK, 14,
                         anchor_x="center", width=380, multiline=True)

        letras = "ABCD"

        for i, r in enumerate(self.botones):

            color = arcade.color.LIGHT_GRAY
            if self.res is not None:
                color = arcade.color.APPLE_GREEN if i == self.ok else arcade.color.LIGHT_GRAY
                if i == self.res and i != self.ok:
                    color = arcade.color.RED

            arcade.draw_rect_filled(r, color)
            arcade.draw_rect_outline(r, arcade.color.BLACK)

            arcade.draw_text(f"{letras[i]}) {self.ops[i]}",
                             r.x + 8, r.y + 8,
                             arcade.color.BLACK, 12)

    def on_mouse_press(self, x, y, *_):
        if self.res is not None:
            self.close()
            return

        for i, r in enumerate(self.botones):
            if r.x < x < r.x+r.width and r.y < y < r.y+r.height:
                self.res = i


# ---------------- FUNCIÓN SIMPLE ----------------
def lanzar_pregunta_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        datos = random.choice(json.load(f))

    VentanaPregunta(datos)
    arcade.run()