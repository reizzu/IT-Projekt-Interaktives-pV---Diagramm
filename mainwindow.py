import tkinter as tk #importiert tkinter für GUI

class simulator: 
    def __init__(self, root): #initialisierung titel, größe, farbe auf dunkelblau
        self.root = root
        self.root.title("pV-Diagramm Simulator")
        self.root.geometry("600x600")
        self.root.configure(bg="#2c3e50")

        tk.Label(root, text="Druck in Bar:", bg="#2c3e50", fg="white").pack() #textlabel und eingabefeld für Druck
        self.ent_p = tk.Entry(root, borderwidth=0)
        self.ent_p.pack(pady=5) #vertikalen Abstand

        tk.Label(root, text="Volumen in m3:", bg="#2c3e50", fg="white").pack()
        self.ent_v = tk.Entry(root, borderwidth=0)
        self.ent_v.pack(pady=5)

        self.prozess_var = tk.StringVar(value="IT")
        tk.OptionMenu(root, self.prozess_var, "IT", "IB", "IC").pack(pady=5) #option menu für die Prozesse, mit Standard IT

        tk.Button(root, text="Zeichnen", command=self.update_view, #Zeichnen Buton, wenn gedrückt wird selfupdateview ausgeführt
                  bg="#27ae60", fg="white", borderwidth=0).pack(pady=10)

        self.canvas = tk.Canvas(root, width=400, height=300, bg="white", highlightthickness=0) #erstellt canvas
        self.canvas.pack(pady=20)
        self.draw_axes() #erstellt Koordinatensystem

    def draw_axes(self): #funktion für Achsen
        self.canvas.create_line(50, 250, 370, 250, width=2, tags="axes")
        self.canvas.create_line(50, 250, 50, 30, width=2, tags="axes")
        self.canvas.create_text(380, 250, text="V", tags="axes", font=("Arial", 10, "bold"))
        self.canvas.create_text(50, 20, text="p", tags="axes", font=("Arial", 10, "bold"))

    def draw_scale(self, min_v, max_v, min_p, max_p, scale_x, scale_y):
        self.canvas.delete("scale")

        # X-Achse Markierungen
        v_steps = 5
        for i in range(v_steps + 1):
            v_val = min_v + i * (max_v - min_v) / v_steps
            x = 60 + (v_val - min_v) * scale_x
            # Strich
            self.canvas.create_line(x, 248, x, 255, width=1, tags="scale")
            # Beschriftung
            self.canvas.create_text(x, 265, text=f"{v_val:.1f}",
                                    font=("Arial", 7), tags="scale")

        # Y-Achse Markierungen
        p_steps = 5
        for i in range(p_steps + 1):
            p_val = min_p + i * (max_p - min_p) / p_steps
            y = 240 - (p_val - min_p) * scale_y
            # Strich
            self.canvas.create_line(48, y, 55, y, width=1, tags="scale")
            # Beschriftung
            self.canvas.create_text(35, y, text=f"{p_val:.1f}",
                                    font=("Arial", 7), tags="scale")

    def update_view(self): #update logic
        self.canvas.delete("plot")
        self.canvas.delete("scale") #alte Zeichnungen gelöscht
        try:
            p_start = float(self.ent_p.get())
            v_start = float(self.ent_v.get()) #holt Werte aus den Eingabefeldern und wandelt sie in float um.

            typ = self.prozess_var.get()

            # Alle Punkte zuerst berechnen
            alle_v = [v_start]
            alle_p = [p_start]

            for i in range(1, 11): #schleife die 10 Pkt berechnet
                step = i * 2
                if typ == "IT": #isotherm pv Konstant
                    v_new = v_start + step
                    if v_new == 0:
                        v_new = 0.1
                    p_new = (p_start * v_start) / v_new
                elif typ == "IB": #isobar p konstant v steigt
                    v_new = v_start + step
                    p_new = p_start
                else:  # isochor V konstant p steigt
                    v_new = v_start
                    p_new = p_start + step

                alle_v.append(v_new)
                alle_p.append(p_new)

            # Scale berechnen
            max_v = max(alle_v)
            max_p = max(alle_p)
            min_v = min(alle_v)
            min_p = min(alle_p)

            scale_x = 280 / (max_v - min_v + 1)
            scale_y = 180 / (max_p - min_p + 1)

            # Achsenbeschriftung zeichnen
            self.draw_scale(min_v, max_v, min_p, max_p, scale_x, scale_y)

            # Punkte in Koordinaten umrechnen
            def to_canvas(v, p):
                x = 60 + (v - min_v) * scale_x
                y = 240 - (p - min_p) * scale_y
                return x, y

            punkte = []
            for v, p in zip(alle_v, alle_p):
                x, y = to_canvas(v, p)
                punkte.extend([x, y])

            self.canvas.create_line(punkte, fill="#3498db", width=3, #punkte werden verbunden und mit blau gezeichnet
                                    tags="plot", smooth=True)

        except ValueError: #wenn Text statt Zahl eingegeben
            pass

root = tk.Tk() #hauptfenster start
app = simulator(root) #instanz
root.mainloop() #hält programm am Laufen
