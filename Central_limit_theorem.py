import tkinter as tk
import random

# Parámetros de la simulación
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
BALL_RADIUS = 4
UPDATE_DELAY = 200  # en milisegundos
PIN_Y_COORDINATE = 100
N_BINS = 25
BIN_LINE_WIDTH = 2
BIN_LINE_HEIGHT = 250
BIN_WIDTH = (CANVAS_WIDTH - (N_BINS-1)*BIN_LINE_WIDTH) // N_BINS
PIN_RADIUS = 8
PIN_SPACE = BIN_WIDTH + BIN_LINE_WIDTH
PIN_ROWS = 5
TOP_HEIGHT = PIN_Y_COORDINATE - PIN_RADIUS
X_STEP_SIZE = PIN_SPACE
Y_STEP_SIZE = PIN_SPACE
N_BALLS = 100
BALLS_ADDED_PER_TICK = 1
INITIAL_BALL_SPREAD = 20 #Pixels

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
                    
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Botón Reiniciar
        self.restart_button = tk.Button(self.button_frame, text="Reiniciar", command=self.restart_simulation)
        self.restart_button.grid(row=0, column=0, padx=5)

        # Segundo botón (sin función por ahora)
        self.extra_button = tk.Button(self.button_frame, text="Start/Stop", command=self.stop_simulation)
        self.extra_button.grid(row=0, column=1, padx=5)

        # Posición inicial en el centro
        self.x = CANVAS_WIDTH // 2
        self.y = BALL_RADIUS + 20

        # Dibujamos las pelotas
        self.balls = []
        for i in range(N_BALLS):
            x = self.x + random.choice(range(-INITIAL_BALL_SPREAD,INITIAL_BALL_SPREAD))
            y = self.y + random.choice(range(-INITIAL_BALL_SPREAD,INITIAL_BALL_SPREAD))
            self.balls.append(self.canvas.create_oval(
                x - BALL_RADIUS, y - BALL_RADIUS,
                x + BALL_RADIUS, y + BALL_RADIUS,
                fill="white"
            ))

        # Controla el descenso de las pelotitas de a poco
        self.fall_index = 1

        # Control de animación
        self.running = True
        self.after_id = None
        self.update_position()

    def update_position(self):

        for ball in self.balls[:self.fall_index]:
            present_x = self.canvas.bbox(ball)[0] + BALL_RADIUS
            present_y = self.canvas.bbox(ball)[1] + BALL_RADIUS

            dy = Y_STEP_SIZE
            new_y = present_y + dy

            # Evitar que salga del canvas
            if BALL_RADIUS <= new_y <= CANVAS_HEIGHT - BALL_RADIUS:
                present_y = new_y
                # Incremento de x por defecto, la pelotita sigue en línea recta hacia abajo a menos que se produzca una colisión
                dx = 0
                if check_collision(ball, self.pines, self.canvas):
                    dx = random.choice([-X_STEP_SIZE, X_STEP_SIZE])
                if check_collision(ball, self.container_bars, self.canvas):
                    dx = BALL_RADIUS

                new_x = present_x + dx
                if BALL_RADIUS <= new_x <= CANVAS_WIDTH - BALL_RADIUS:
                    present_x = new_x
            
                # Mover la pelotita si no ha colisionado con otra pelotita.
                if present_y < CANVAS_HEIGHT - BIN_LINE_HEIGHT or check_collision(ball, self.balls[: self.fall_index], self.canvas):
                    self.canvas.coords(
                        ball,
                        present_x - BALL_RADIUS, present_y - BALL_RADIUS,
                        present_x + BALL_RADIUS, present_y + BALL_RADIUS
                    )


        self.fall_index = self.fall_index + BALLS_ADDED_PER_TICK

        # Llamar de nuevo a esta función luego de un retardo
        # Guardar ID del próximo evento programado
        self.after_id = self.root.after(UPDATE_DELAY, self.update_position)


    def stop_simulation(self):
        # Detener animación actual
        if self.running:
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.running = False
        else:
            self.running = True
            self.update_position()

        
    
    def restart_simulation(self):
        # Detener animación actual
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        # Resetear posición
        self.x = CANVAS_WIDTH // 2
        self.y = BALL_RADIUS

         # Borramos las pelotas
        for ball in self.balls:
            self.canvas.delete(ball)

         # Dibujamos las pelotas
        self.balls = []
        for i in range(N_BALLS):
            x = self.x + random.choice(range(-INITIAL_BALL_SPREAD, INITIAL_BALL_SPREAD))
            y = self.y + random.choice(range(-INITIAL_BALL_SPREAD, INITIAL_BALL_SPREAD))
            self.balls.append(self.canvas.create_oval(
                x - BALL_RADIUS, y - BALL_RADIUS,
                x + BALL_RADIUS, y + BALL_RADIUS,
                fill="white"
            ))
        self.fall_index = 1

        # Reiniciar
        self.running = True
        self.update_position()


# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = board_app(root)
    root.mainloop()
