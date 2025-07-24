import tkinter as tk
import random

# Parámetros de la simulación
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
BALL_RADIUS = 4
UPDATE_DELAY = 80  # en milisegundos
PIN_Y_COORDINATE = 100
N_BINS = 25
BIN_LINE_WIDTH = 2
BIN_LINE_HEIGHT = 250
BIN_WIDTH = (CANVAS_WIDTH - (N_BINS-1)*BIN_LINE_WIDTH) // N_BINS
PIN_RADIUS = 8
PIN_SPACE = BIN_WIDTH + BIN_LINE_WIDTH
PIN_ROWS = 5
TOP_HEIGHT = PIN_Y_COORDINATE - PIN_RADIUS
STEP_SIZE = PIN_SPACE

# Check for intersection
def check_collision(ball, bbox_list, canvas):
    test = False
    bbox_ball = canvas.bbox(ball)
    for item in bbox_list:
        bbox_from_list = canvas.bbox(item)
        test = test or not (
            bbox_ball[2] < bbox_from_list[0] or   # bbox1 right < bbox2 left
            bbox_ball[0] > bbox_from_list[2] or   # bbox1 left > bbox2 right
            bbox_ball[3] < bbox_from_list[1] or   # bbox1 bottom < bbox2 top
            bbox_ball[1] > bbox_from_list[3]      # bbox1 top > bbox2 bottom
        )
    return test
        



class board_app:
    def __init__(self, root):
        self.root = root
        self.root.title("Galton Board")

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black")
        self.canvas.pack()

        # Contenedores
        self.container_bars = []
        for i in range(1, N_BINS):
            x_coordinate = i*(BIN_WIDTH + BIN_LINE_WIDTH)
            y1_coordinate = CANVAS_HEIGHT
            y2_coordinate = CANVAS_HEIGHT - BIN_LINE_HEIGHT
            self.container_bars.append(self.canvas.create_line(x_coordinate, y1_coordinate, x_coordinate, y2_coordinate, fill="green", width=BIN_LINE_WIDTH))
            
        # Pines
        self.pines = []
        for j in range(PIN_ROWS):
            for i in range(1, N_BINS):
                x_coordinate = i*PIN_SPACE
                y_coordinate = PIN_Y_COORDINATE + j*2*PIN_SPACE
                if i % 2 == 0:
                    y_coordinate = y_coordinate + PIN_SPACE
                    self.pines.append(self.canvas.create_oval(x_coordinate - PIN_RADIUS, y_coordinate - PIN_RADIUS, 
                                        x_coordinate + PIN_RADIUS, y_coordinate + PIN_RADIUS, 
                                        fill="green"))
                else:
                    self.pines.append(self.canvas.create_oval(x_coordinate - PIN_RADIUS, y_coordinate - PIN_RADIUS, 
                                        x_coordinate + PIN_RADIUS, y_coordinate + PIN_RADIUS, 
                                        fill="green"))
                    
        # Botón de reinicio
        self.restart_button = tk.Button(root, text="Reiniciar", command=self.restart_simulation)
        self.restart_button.pack(pady=10)

        # Posición inicial en el centro
        self.x = CANVAS_WIDTH // 2
        self.y = BALL_RADIUS

        # Dibujamos la pelota
        self.ball = self.canvas.create_oval(
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS,
            fill="white"
        )

        # Control de animación
        self.running = True
        self.after_id = None
        self.update_position()

    def update_position(self):
        
        dy = STEP_SIZE
        new_y = self.y + dy

        # Evitar que salga del canvas
        if BALL_RADIUS <= new_y <= CANVAS_HEIGHT - BALL_RADIUS:
            self.y = new_y
            # Agregar comentario
            if check_collision(self.ball, self.pines, self.canvas):
                dx = random.choice([-STEP_SIZE, STEP_SIZE])
            else:
                dx = 0
            new_x = self.x + dx
            if BALL_RADIUS <= new_x <= CANVAS_WIDTH - BALL_RADIUS:
                self.x = new_x

        # Mover la pelotita
        self.canvas.coords(
            self.ball,
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS
        )

        # Llamar de nuevo a esta función luego de un retardo
        # Guardar ID del próximo evento programado
        self.after_id = self.root.after(UPDATE_DELAY, self.update_position)
    
    def restart_simulation(self):
        # Detener animación actual
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        # Resetear posición
        self.x = CANVAS_WIDTH // 2
        self.y = BALL_RADIUS
        self.canvas.coords(
            self.ball,
            self.x - BALL_RADIUS, self.y - BALL_RADIUS,
            self.x + BALL_RADIUS, self.y + BALL_RADIUS
        )

        # Reiniciar
        self.running = True
        self.update_position()


# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = board_app(root)
    root.mainloop()
