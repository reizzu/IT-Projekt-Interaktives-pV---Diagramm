import math
import tkinter as tk        
from tkinter import ttk

#FARBEN
BG        = "#0d0f14"
PANEL     = "#13161e"
CARD      = "#1a1e2a"
BORDER    = "#252a38"
ACCENT    = "#008000"
ACCENT2   = "#7c6af7"
TEXT      = "#e8eaf0"
TEXT_DIM  = "#5c6380"
TEXT_MID  = "#9ba3bf"

def start_simulation():
    print(f"Starte Simulation...")
    # code hier rein
    
#-------MAIN PAGE
root = tk.Tk()
root.title("pV-Diagramm Simulator")
root.geometry("600x500")
root.configure(bg=BG)

# Header
title = tk.Label(root, text="GAS KONFIGURATOR", font=("Arial", 18, "bold"), bg=BG, fg=TEXT)
title.pack(pady=20)

#START BUTTON
btn_start = tk.Button(root, text="Simulation Starten →", state="active",
                      bg=ACCENT, fg=TEXT, font=("Arial", 12, "bold"),
                      padx=20, pady=10, command=start_simulation)
btn_start.pack(pady=10)

root.mainloop()
