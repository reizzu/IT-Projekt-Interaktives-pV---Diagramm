import tkinter as tk #importiert tkinter für GUI

class simulator: 
    def __init__(self, root): #initialisierung titel, größe, farbe auf dunkelblau
        self.root = root
        self.root.title("pV-Diagramm Simulator")
        self.root.geometry("600x700")
        self.root.configure(bg="#2c3e50")

        # Zustands-Speicher für die Klicks
        self.start_zustand = None
        self.end_zustand = None

        tk.Label(root, text="Druck in Bar:", bg="#2c3e50", fg="white").pack() #textlabel für live anzeige Druck
        self.ent_p = tk.Entry(root, borderwidth=0)
        self.ent_p.pack(pady=5) #vertikalen Abstand

        tk.Label(root, text="Volumen in m3:", bg="#2c3e50", fg="white").pack()
        self.ent_v = tk.Entry(root, borderwidth=0)
        self.ent_v.pack(pady=5)

        tk.Label(root, text="Klicke in das Diagramm für Start und Ende:", bg="#2c3e50", fg="#f1c40f").pack(pady=5)

        self.prozess_var = tk.StringVar(value="IT (Isotherm -> Isochor)")
        tk.OptionMenu(root, self.prozess_var, "IT (Isotherm -> Isochor)", "IB (Isobar -> Isochor)", "IC (Isochor -> Isobar)").pack(pady=5)

        tk.Button(root, text="Zeichnen", command=self.update_view, #Zeichnen Buton, wenn gedrückt wird selfupdateview ausgeführt
                  bg="#27ae60", fg="white", borderwidth=0).pack(pady=10)

        self.canvas = tk.Canvas(root, width=400, height=300, bg="white", highlightthickness=0) #erstellt canvas
        self.canvas.pack(pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click) # Bindet Mausklick an Canvas
        
        self.draw_axes() #erstellt Koordinatensystem
        self.draw_scale() # Zeichnet die Skala sofort beim Start

    def on_canvas_click(self, event): # logik für Klicks
        # wenn schon 2 Punkte da sind lösche alles für neuen Versuch
        if self.start_zustand and self.end_zustand:
            self.start_zustand = None
            self.end_zustand = None
            self.canvas.delete("points")
            self.canvas.delete("plot")

        # Umrechnung Pixel in Einheiten (x-Achse=15px, y-Achse=10px pro Einheit)
        v = (event.x - 50) / 15
        p = (250 - event.y) / 10
        if v < 0.1: v = 0.1 # Verhindert, dass das Volumen 0 wird
        if p < 0.1: p = 0.1
        
        #Live-Anzeige
        self.ent_v.delete(0, tk.END) # Löscht den alten Wert im Feld
        self.ent_v.insert(0, f"{v:.1f}") # Schreibt das neue Volumen mit 1 Nachkommastelle rein
        self.ent_p.delete(0, tk.END)
        self.ent_p.insert(0, f"{p:.1f}")


        if not self.start_zustand:
            self.start_zustand = (v, p)
            self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="green", tags="points")
        else:
            self.end_zustand = (v, p)
            self.canvas.create_oval(event.x-4, event.y-4, event.x+4, event.y+4, fill="red", tags="points")
            self.update_view() # Automatisch zeichnen wenn 2. Punkt gesetzt

    def draw_axes(self): #funktion für Achsen
        self.canvas.create_line(50, 250, 370, 250, width=2, tags="axes")
        self.canvas.create_line(50, 250, 50, 30, width=2, tags="axes")
        self.canvas.create_text(380, 250, text="V", tags="axes", font=("Arial", 10, "bold"))
        self.canvas.create_text(50, 20, text="p", tags="axes", font=("Arial", 10, "bold"))

    def draw_scale(self):
        self.canvas.delete("scale")
        # Feste Skala zeichnen (0 bis 20 Einheiten)
        for i in range(0, 21, 5):
            # X-Achse (Volumen)
            x = 50 + i * 15 
            self.canvas.create_line(x, 248, x, 255, width=1, tags="scale")
            if i > 0: self.canvas.create_text(x, 265, text=str(i), font=("Arial", 7), tags="scale")
            
            # Y-Achse (Druck)
            y = 250 - i * 10 
            self.canvas.create_line(48, y, 55, y, width=1, tags="scale")
            if i > 0: self.canvas.create_text(35, y, text=str(i), font=("Arial", 7), tags="scale")

    def update_view(self): #update logic
        self.canvas.delete("plot") #alte Zeichnungen gelöscht
        
        # Falls Klicks vorhanden sonst die Eingabefelder
        if self.start_zustand and self.end_zustand:
            v_start, p_start = self.start_zustand
            v_ziel, p_ziel = self.end_zustand
        else:
            try:
                p_start = float(self.ent_p.get()) #holt Werte aus den Eingabefeldern und wandelt sie in float um.
                v_start = float(self.ent_v.get())
                p_ziel, v_ziel = p_start * 0.5, v_start * 2 # Standard-Ziel für Eingabefelder
            except ValueError: return #wenn Text statt Zahl eingegeben

        typ = self.prozess_var.get()
        alle_v = []
        alle_p = []

        if "IT" in typ: #isotherm pv Konstant -> dann isochor zum Ziel
            for i in range(11): #schleife die 10 Pkt berechnet
                t = i / 10.0
                v_new = v_start + (v_ziel - v_start) * t
                if v_new == 0: v_new = 0.1
                p_new = (p_start * v_start) / v_new
                alle_v.append(v_new)
                alle_p.append(p_new)
            alle_v.append(v_ziel) # Isochorer Ausgleichsschritt genau zum Endpunkt
            alle_p.append(p_ziel)
            
        elif "IB" in typ: #isobar p konstant v steigt -> dann isochor zum Ziel
            alle_v.extend([v_start, v_ziel, v_ziel])
            alle_p.extend([p_start, p_start, p_ziel])
            
        else: # isochor V konstant p steigt -> dann isobar zum Ziel
            alle_v.extend([v_start, v_start, v_ziel])
            alle_p.extend([p_start, p_ziel, p_ziel])

        # Punkte in Koordinaten umrechnen
        def to_canvas(v, p):
            return 50 + v * 15, 250 - p * 10

        punkte = []
        for v, p in zip(alle_v, alle_p):
            x, y = to_canvas(v, p)
            punkte.extend([x, y])

        self.canvas.create_line(punkte, fill="#3498db", width=3, #punkte werden verbunden und mit blau gezeichnet
                                tags="plot") 

root = tk.Tk() #hauptfenster start
app = simulator(root) #instanz
root.mainloop() #hält programm am Laufen
