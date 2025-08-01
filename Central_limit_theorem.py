import tkinter as tk
import random
from scipy.stats import norm
import numpy as np

# Parámetros de la simulación
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
BALL_RADIUS = 3
UPDATE_DELAY = 100  # en milisegundos
PIN_Y_COORDINATE = 100
BIN_LINE_WIDTH = 2 # Multiplos de 2
BIN_LINE_HEIGHT = 250
PIN_RADIUS = 12
PIN_SPACE = 24
PIN_ROWS = 5
PIN_COLUMNS = 25
N_BINS = PIN_COLUMNS
TOP_HEIGHT = PIN_Y_COORDINATE - PIN_RADIUS
Y_STEP_SIZE = 7
N_BALLS = 900
BALLS_ADDED_PER_TICK = 2
TICKS_TO_FALL = 10
INITIAL_BALL_SPREAD = 5 #Pixels
X_BALLS_INIT = 12*PIN_SPACE
# to adjusto de bell curve amplitude
BELL_AMPLITUDE = 50000

# Check for intersection
def check_collision(ball, bbox_list, canvas):
    test = False
    bbox_ball = canvas.bbox(ball)
    for item in bbox_list:
        bbox_from_list = canvas.bbox(item)
        test  = not (
            bbox_ball[2] < bbox_from_list[0] or   # bbox1 right < bbox2 left
            bbox_ball[0] > bbox_from_list[2] or   # bbox1 left > bbox2 right
            bbox_ball[3] < bbox_from_list[1] or   # bbox1 bottom < bbox2 top
            bbox_ball[1] > bbox_from_list[3]      # bbox1 top > bbox2 bottom
        )
        if test:
            return bbox_from_list
    return False

        
class board_app:
    def __init__(self, root):
        self.root = root
        self.root.title("Galton Board")

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black")
        self.canvas.pack()

        # Separadores de Contenedores
        self.container_bars = []
        for i in range(0, PIN_COLUMNS):
            if i % 2:
                x_coordinate = i*PIN_SPACE - BIN_LINE_WIDTH // 2
                y1_coordinate = CANVAS_HEIGHT
                y2_coordinate = CANVAS_HEIGHT - BIN_LINE_HEIGHT
                self.container_bars.append(self.canvas.create_line(x_coordinate, y1_coordinate, x_coordinate, y2_coordinate, fill="green", width=BIN_LINE_WIDTH))

        # Contenedores, es una lista que contiene las pelotiras en cada bin
        self.balls_in_bins = [[] for i in range(N_BINS)]
    
        # Pines
        self.pines = []
        for j in range(PIN_ROWS):
            for i in range(1, PIN_COLUMNS):
                x_coordinate = i*PIN_SPACE
                y_coordinate = PIN_Y_COORDINATE + j*2*PIN_SPACE
                if i % 2 == 0:
                    self.pines.append(self.canvas.create_oval(x_coordinate - PIN_RADIUS, y_coordinate - PIN_RADIUS, 
                                        x_coordinate + PIN_RADIUS, y_coordinate + PIN_RADIUS, 
                                        fill="green"))
                else:
                    
                    y_coordinate = y_coordinate + PIN_SPACE
                    self.pines.append(self.canvas.create_oval(x_coordinate - PIN_RADIUS, y_coordinate - PIN_RADIUS, 
                                        x_coordinate + PIN_RADIUS, y_coordinate + PIN_RADIUS, 
                                        fill="green"))
                    
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack(pady=10)

        # Normal Bell shape
        # See the file Galton board model in this repository to check the values for standar deviation and mean
        # Std = delta_x * sqrt(n) = (2*PIN_RADIUS)*(2*PIN_ROWS)**0.5)
        # Where 2*PIN_RADIUS is the x displacement in each kick and 
        x = [i for i in range(600) if i%2]
        y = list(map(lambda j: norm.pdf(j, X_BALLS_INIT, 2*PIN_RADIUS*(2*PIN_ROWS)**0.5), x))
        points = []
        for k in zip(x, y):
            points.append(k[0])
            points.append(CANVAS_HEIGHT - k[1]*BELL_AMPLITUDE)
        self.canvas.create_line(points, fill="yellow", width=3, smooth=True)

        # Botón Reiniciar
        self.restart_button = tk.Button(self.button_frame, text="Reiniciar", command=self.restart_simulation)
        self.restart_button.grid(row=0, column=0, padx=5)

        # Botón start stop
        self.extra_button = tk.Button(self.button_frame, text="Start/Stop", command=self.stop_simulation)
        self.extra_button.grid(row=0, column=1, padx=5)

        # Botón para acelerar
        self.speed_button = tk.Button(self.button_frame, text="Faster", command=self.faster)
        self.speed_button.grid(row=0, column=2, padx=5)

        # Botón para desacelerar
        self.speed_button = tk.Button(self.button_frame, text="Slower", command=self.slower)
        self.speed_button.grid(row=0, column=3, padx=5)

        # Texto para indicar la desviación estandar
        self.label_std = tk.Label(self.info_frame, text=f'Pop. mean: {X_BALLS_INIT}', font=("Arial", 10))
        self.label_std.grid(row=1, column=0, padx=5)
        # Texto para indicar el promedio
        self.info_mean = tk.Label(self.info_frame, text=f'Pop. std: {round(2*PIN_RADIUS*(2*PIN_ROWS)**0.5, 2)}', font=("Arial", 10))
        self.info_mean.grid(row=1, column=1, padx=5)

        # Texto para indicar la desviación estandar
        self.info_smean = tk.Label(self.info_frame, text="Sample mean: ", font=("Arial", 10))
        self.info_smean.grid(row=1, column=2, padx=5)
        # Texto para indicar el promedio
        self.info_sstd = tk.Label(self.info_frame, text="Sample std: ", font=("Arial", 10))
        self.info_sstd.grid(row=1, column=3, padx=5)

        # Posición inicial en el centro
        self.x = X_BALLS_INIT
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

        # Contrala cada cuantos ticks de reloja lanza pelotitas
        self.fall_sequence = 0

        # Delay inicial
        self.delay = UPDATE_DELAY

        # Control de animación
        self.running = True
        self.after_id = None
        self.update_position()

        # Acumulador para calcular la desviación estandar
        self.x_samples = []

    def get_bin_number(self, ball):
        ball_bbox = self.canvas.bbox(ball)
        n = int((ball_bbox[0] - PIN_SPACE - BIN_LINE_WIDTH) //  (2*PIN_SPACE + BIN_LINE_WIDTH))
        return n
    
    def get_bin_coords(self, n):
        x = (n+1)*2*PIN_SPACE + n*BIN_LINE_WIDTH
        y = CANVAS_HEIGHT
        return x, y
    
    def place_ball_in_bin(self, nbin, ball):
        l = len(self.balls_in_bins[nbin])
        column = l % 5
        h = (l // 5) * 2 * BALL_RADIUS 
        X, Y = self.get_bin_coords(nbin)
        if l == 0:
            self.canvas.coords(
                        ball,
                        X - 2*BALL_RADIUS, Y - 2*BALL_RADIUS,
                        X, Y
                    )
        elif column == 0:
            self.canvas.coords(
                        ball,
                        X - 2*BALL_RADIUS, Y - h - 2*BALL_RADIUS,
                        X, Y - h
                    )
        elif column == 1:
            self.canvas.coords(
                        ball,
                        X - 4*BALL_RADIUS, Y - h - 2*BALL_RADIUS,
                        X - 2*BALL_RADIUS, Y - h
                    )
        elif column == 2:
            self.canvas.coords(
                        ball,
                        X - 6*BALL_RADIUS, Y - h - 2*BALL_RADIUS,
                        X - 4*BALL_RADIUS, Y - h
                    )
        elif column == 3:
            self.canvas.coords(
                        ball,
                        X - 8*BALL_RADIUS, Y - h - 2*BALL_RADIUS,
                        X - 6*BALL_RADIUS, Y - h
                    )
        elif column == 4:
            self.canvas.coords(
                        ball,
                        X - 10*BALL_RADIUS, Y - h - 2*BALL_RADIUS,
                        X - 8*BALL_RADIUS, Y - h
                    )
        self.balls_in_bins[nbin].append(ball)    

    def update_position(self):

        for ball in self.balls[:self.fall_index]:
            #Hay una diferencia de un pixel de menos entre la coordenada obtenida con canvas.bbox y la seteada con canvas.coords 
            present_x = self.canvas.bbox(ball)[0] + BALL_RADIUS + 1
            present_y = self.canvas.bbox(ball)[1] + BALL_RADIUS + 1
            
            dy = Y_STEP_SIZE
            # Siempre desciende
            new_y = present_y + dy
            # Incremento de x = 0 por defecto, la pelotita sigue en línea recta hacia abajo a menos que se produzca una colisión
            new_x = present_x

            # Evitar que salga del canvas
            if BALL_RADIUS <= new_y <= CANVAS_HEIGHT - BALL_RADIUS:
                #Por defecto hay solo un incremento dy
                present_y = new_y
                colided = check_collision(ball, self.pines, self.canvas)
                if colided:
                    direction = random.choice(['left', 'right'])
                    if direction == 'left':
                        new_x = colided[0] - PIN_RADIUS
                    elif direction == 'right':
                        new_x = colided[2] + PIN_RADIUS
                    # El avance en y es el mínimo necesario para no colicionar con el pin contiguo al colisionado original
                    present_y = colided[3] - dy

                colided = check_collision(ball, self.container_bars, self.canvas)        
                if colided:
                    if self.canvas.bbox(ball)[2] > colided[0]:
                        new_x = colided[0] - BIN_LINE_WIDTH
                    elif self.canvas.bbox(ball)[0] < colided[2]:
                        new_x = colided[2] + BIN_LINE_WIDTH


                # Se mueve en x solo si no ha llegado al límite del canvas
                if BALL_RADIUS <= new_x <= CANVAS_WIDTH - BALL_RADIUS:
                    present_x = new_x
        
                # Mover la pelotita si no ha colisionado con otra pelotita o si se encuentra en la parte superior de su compartimento
                nbin = self.get_bin_number(ball)
                bin_height = (len(self.balls_in_bins[nbin]) // 5)*2*BALL_RADIUS + 2*BALL_RADIUS
                if present_y < CANVAS_HEIGHT - bin_height:
                    self.canvas.coords(
                        ball,
                        present_x - BALL_RADIUS, present_y - BALL_RADIUS,
                        present_x + BALL_RADIUS, present_y + BALL_RADIUS
                    )
                else:
                    self.x_samples.append(present_x)
                    n = self.get_bin_number(ball)
                    self.place_ball_in_bin(n, ball)
                    self.balls.pop(self.balls.index(ball))
                    self.info_sstd.config(text=f'Sample std: {round(np.std(self.x_samples, ddof=1), 2)}')
                    self.info_smean.config(text=f'Sample mean: {round(np.mean(self.x_samples), 2)}')


                    
        self.fall_sequence += 1
        if self.fall_sequence >= TICKS_TO_FALL:
            self.fall_sequence = 0
            self.fall_index = self.fall_index + BALLS_ADDED_PER_TICK

        # Llamar de nuevo a esta función luego de un retardo
        # Guardar ID del próximo evento programado
        self.after_id = self.root.after(self.delay, self.update_position)


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
        self.x = X_BALLS_INIT
        self.y = BALL_RADIUS

        # Reinicia el delay
        self.delay = UPDATE_DELAY

        # Resetear los labels
        self.info_sstd.config(text=f'Sample std: ')
        self.info_smean.config(text=f'Sample mean: ')


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

        # Se vacian los contenedores.
        for bin in self.balls_in_bins:
            for ball in bin:
                self.canvas.delete(ball)
        
        self.balls_in_bins = [[] for i in range(N_BINS) ]

        # Reiniciar
        self.running = True
        self.update_position()

    def faster(self):
        if self.delay > 1:
            self.delay = self.delay // 2
        
    def slower(self):
        if self.delay < 2000:
            self.delay = self.delay*2

# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = board_app(root)
    root.mainloop()
