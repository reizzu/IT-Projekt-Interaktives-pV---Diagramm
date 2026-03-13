import tkinter as tk
from tkinter import ttk, font
import math

# ── Colour palette ──────────────────────────────────────────────────────────
BG        = "#0d0f14"
PANEL     = "#13161e"
CARD      = "#1a1e2a"
BORDER    = "#252a38"
ACCENT    = "#4f9cf9"
ACCENT2   = "#7c6af7"
TEXT      = "#e8eaf0"
TEXT_DIM  = "#5c6380"
TEXT_MID  = "#9ba3bf"

COL_ISO_V = "#4f9cf9"   # isochoric  – blue
COL_ISO_P = "#f97b4f"   # isobaric   – orange
COL_ISO_T = "#4fda9a"   # isothermal – green
COL_ADIAB = "#c96af7"   # adiabatic  – purple

# ── Physics constants ────────────────────────────────────────────────────────
GAMMA = 1.4   # Cp/Cv for diatomic ideal gas

# ── Canvas world coords ──────────────────────────────────────────────────────
V_MIN, V_MAX = 0.5, 5.0
P_MIN, P_MAX = 0.5, 5.0

class PVDiagram:
    def __init__(self, root):
        self.root = root
        root.title("pV – Diagramm  |  Ideales Gas")
        root.configure(bg=BG)
        root.geometry("1100x720")
        root.minsize(900, 600)
        root.resizable(True, True)

        self.state1 = None   # (p, V)
        self.state2 = None
        self.click_mode = 1  # next click sets state 1 or 2

        self._build_ui()
        self._draw_grid()

    # ── UI skeleton ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # header
        hdr = tk.Frame(self.root, bg=BG, height=52)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="pV", bg=BG, fg=ACCENT,
                 font=("Georgia", 20, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(hdr, text="Interaktives Diagramm — Ideales Gas",
                 bg=BG, fg=TEXT_MID,
                 font=("Courier New", 11)).pack(side="left", pady=10)

        btn_reset = tk.Button(hdr, text="⟳  Reset", bg=CARD, fg=TEXT,
                              activebackground=BORDER, activeforeground=TEXT,
                              relief="flat", bd=0, padx=14, pady=6,
                              font=("Courier New", 10),
                              cursor="hand2", command=self._reset)
        btn_reset.pack(side="right", padx=16, pady=10)

        # separator
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")

        # main body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # canvas frame
        cf = tk.Frame(body, bg=PANEL, bd=0, highlightthickness=0)
        cf.pack(side="left", fill="both", expand=True, padx=(16,8), pady=16)

        self.canvas = tk.Canvas(cf, bg=BG, bd=0, highlightthickness=1,
                                highlightbackground=BORDER, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True, padx=1, pady=1)
        self.canvas.bind("<Configure>", lambda e: self._redraw())
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>",   self._on_hover)

        # right panel
        rp = tk.Frame(body, bg=BG, width=260)
        rp.pack(side="right", fill="y", padx=(0,16), pady=16)
        rp.pack_propagate(False)
        self._build_right_panel(rp)

    def _build_right_panel(self, parent):
        def section(title):
            tk.Label(parent, text=title, bg=BG, fg=TEXT_DIM,
                     font=("Courier New", 8)).pack(anchor="w", pady=(14,4))
            tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        # ── Instructions ────────────────────────────────────────────────────
        section("ANLEITUNG")
        self.instr_lbl = tk.Label(parent,
            text="① Klicke auf das Diagramm\n   um Zustand 1 zu setzen",
            bg=BG, fg=TEXT_MID, font=("Courier New", 10),
            justify="left", wraplength=230)
        self.instr_lbl.pack(anchor="w", pady=6)

        # ── States ───────────────────────────────────────────────────────────
        section("ZUSTÄNDE")
        self.s1_lbl = self._state_card(parent, "1", ACCENT)
        self.s2_lbl = self._state_card(parent, "2", ACCENT2)

        # ── Legend ───────────────────────────────────────────────────────────
        section("PROZESSPFADE")
        paths = [
            (COL_ISO_V, "Isochor",    "V = const"),
            (COL_ISO_P, "Isobar",     "p = const"),
            (COL_ISO_T, "Isotherm",   "T = const"),
            (COL_ADIAB, "Adiabatisch","Q = 0"),
        ]
        for col, name, eq in paths:
            row = tk.Frame(parent, bg=BG)
            row.pack(fill="x", pady=3)
            tk.Canvas(row, bg=BG, width=28, height=14,
                      bd=0, highlightthickness=0).pack(side="left")
            c = row.winfo_children()[0]
            c.create_line(0, 7, 28, 7, fill=col, width=2.5)
            tk.Label(row, text=name, bg=BG, fg=TEXT,
                     font=("Courier New", 10, "bold")).pack(side="left")
            tk.Label(row, text=f"  {eq}", bg=BG, fg=TEXT_DIM,
                     font=("Courier New", 9)).pack(side="left")

        # ── Work results ─────────────────────────────────────────────────────
        section("ARBEIT  W = ∫p dV")
        self.work_frame = tk.Frame(parent, bg=BG)
        self.work_frame.pack(fill="x")
        self._work_labels = {}
        for col, name, _ in paths:
            row = tk.Frame(self.work_frame, bg=CARD,
                           highlightthickness=1, highlightbackground=BORDER)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=name, bg=CARD, fg=col,
                     font=("Courier New", 9, "bold"),
                     width=13, anchor="w").pack(side="left", padx=8, pady=5)
            lbl = tk.Label(row, text="—", bg=CARD, fg=TEXT_MID,
                           font=("Courier New", 9))
            lbl.pack(side="right", padx=8)
            self._work_labels[name] = lbl

        # hover coords
        section("CURSOR")
        self.coord_lbl = tk.Label(parent, text="p = —   V = —",
                                  bg=BG, fg=TEXT_DIM,
                                  font=("Courier New", 10))
        self.coord_lbl.pack(anchor="w", pady=4)

    def _state_card(self, parent, num, color):
        row = tk.Frame(parent, bg=CARD,
                       highlightthickness=1, highlightbackground=BORDER)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=f" {num} ", bg=color, fg=BG,
                 font=("Courier New", 10, "bold")).pack(side="left")
        lbl = tk.Label(row, text="  nicht gesetzt",
                       bg=CARD, fg=TEXT_DIM,
                       font=("Courier New", 10))
        lbl.pack(side="left", padx=6, pady=6)
        return lbl

    # ── Coordinate transforms ────────────────────────────────────────────────
    def _margins(self):
        return dict(left=54, right=20, top=20, bottom=48)

    def _w2c(self, V, p):
        """World (V,p) → canvas (x,y)"""
        m = self._margins()
        W = self.canvas.winfo_width()  or 600
        H = self.canvas.winfo_height() or 480
        cw = W - m["left"] - m["right"]
        ch = H - m["top"]  - m["bottom"]
        x = m["left"] + (V - V_MIN) / (V_MAX - V_MIN) * cw
        y = m["top"]  + (1 - (p - P_MIN) / (P_MAX - P_MIN)) * ch
        return x, y

    def _c2w(self, x, y):
        """Canvas (x,y) → world (V,p)"""
        m = self._margins()
        W = self.canvas.winfo_width()  or 600
        H = self.canvas.winfo_height() or 480
        cw = W - m["left"] - m["right"]
        ch = H - m["top"]  - m["bottom"]
        V = V_MIN + (x - m["left"]) / cw * (V_MAX - V_MIN)
        p = P_MIN + (1 - (y - m["top"]) / ch) * (P_MAX - P_MIN)
        return V, p

    # ── Drawing ──────────────────────────────────────────────────────────────
    def _redraw(self):
        self.canvas.delete("all")
        self._draw_grid()
        if self.state1:
            self._draw_point(self.state1, "1", ACCENT)
        if self.state1 and self.state2:
            self._draw_paths()
            self._draw_point(self.state1, "1", ACCENT)
            self._draw_point(self.state2, "2", ACCENT2)
            self._update_work()

    def _draw_grid(self):
        c = self.canvas
        m = self._margins()
        W = c.winfo_width()  or 600
        H = c.winfo_height() or 480

        # axis background subtle glow
        c.create_rectangle(m["left"], m["top"],
                            W - m["right"], H - m["bottom"],
                            fill="#0a0c12", outline=BORDER)

        # grid lines
        ticks_V = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
        ticks_p = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
        for v in ticks_V:
            x, _ = self._w2c(v, P_MIN)
            _, y0 = self._w2c(v, P_MAX)
            c.create_line(x, y0, x, H - m["bottom"],
                          fill=BORDER, dash=(3,5))
            c.create_text(x, H - m["bottom"] + 14, text=f"{v:.1f}",
                          fill=TEXT_DIM, font=("Courier New", 8))
        for p in ticks_p:
            _, y = self._w2c(V_MIN, p)
            x1, _ = self._w2c(V_MAX, p)
            c.create_line(m["left"], y, x1, y,
                          fill=BORDER, dash=(3,5))
            c.create_text(m["left"] - 14, y, text=f"{p:.1f}",
                          fill=TEXT_DIM, font=("Courier New", 8))

        # axes
        x0, y0 = self._w2c(V_MIN, P_MIN)
        x1, _  = self._w2c(V_MAX, P_MIN)
        _, y1  = self._w2c(V_MIN, P_MAX)
        c.create_line(x0, y0, x1, y0, fill=TEXT_MID, width=1.5)
        c.create_line(x0, y0, x0, y1, fill=TEXT_MID, width=1.5)

        # axis labels
        c.create_text((x0 + x1) / 2, H - 8,
                      text="V  [willk. Einheit]",
                      fill=TEXT_MID, font=("Courier New", 9))
        c.create_text(14, (y0 + y1) / 2,
                      text="p", fill=TEXT_MID,
                      font=("Courier New", 9), angle=90)

    def _draw_point(self, state, label, color):
        p, V = state
        x, y = self._w2c(V, p)
        r = 7
        self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                fill=color, outline=BG, width=2)
        self.canvas.create_text(x + 14, y - 12,
                                text=label, fill=color,
                                font=("Courier New", 10, "bold"))

    def _draw_paths(self):
        p1, V1 = self.state1
        p2, V2 = self.state2
        N = 200

        # isochoric: V=const, p goes from p1→p2 at V=V1, then V→V2 at p2
        pts = []
        for i in range(N+1):
            pv = p1 + (p2 - p1) * i / N
            pts += list(self._w2c(V1, pv))
        for i in range(N+1):
            vv = V1 + (V2 - V1) * i / N
            pts += list(self._w2c(vv, p2))
        self.canvas.create_line(*pts, fill=COL_ISO_V,
                                width=2, smooth=True, dash=(8,4))

        # isobaric: p=const at p1, V goes p1→p2, then p→p2 at V2
        pts = []
        for i in range(N+1):
            vv = V1 + (V2 - V1) * i / N
            pts += list(self._w2c(vv, p1))
        for i in range(N+1):
            pv = p1 + (p2 - p1) * i / N
            pts += list(self._w2c(V2, pv))
        self.canvas.create_line(*pts, fill=COL_ISO_P,
                                width=2, smooth=True, dash=(8,4))

        # isothermal: p*V = const = p1*V1 → then jump to state 2
        T1 = p1 * V1
        pts = []
        for i in range(N+1):
            vv = V1 + (V2 - V1) * i / N
            if vv <= 0: continue
            pv = T1 / vv
            pts += list(self._w2c(vv, pv))
        # connect end of isotherm to state2
        if len(pts) >= 4:
            self.canvas.create_line(*pts, fill=COL_ISO_T, width=2, smooth=True)
        end_V = V2; end_p = T1 / V2 if V2 != 0 else p2
        ex, ey = self._w2c(end_V, end_p)
        x2, y2 = self._w2c(V2, p2)
        self.canvas.create_line(ex, ey, x2, y2,
                                fill=COL_ISO_T, width=2, dash=(4,4))

        # adiabatic: p * V^γ = const = p1 * V1^γ
        C = p1 * (V1 ** GAMMA)
        pts = []
        for i in range(N+1):
            vv = V1 + (V2 - V1) * i / N
            if vv <= 0: continue
            pv = C / (vv ** GAMMA)
            pts += list(self._w2c(vv, pv))
        end_p_ad = C / (V2 ** GAMMA) if V2 > 0 else p2
        if len(pts) >= 4:
            self.canvas.create_line(*pts, fill=COL_ADIAB, width=2, smooth=True)
        ex, ey = self._w2c(V2, end_p_ad)
        x2, y2 = self._w2c(V2, p2)
        self.canvas.create_line(ex, ey, x2, y2,
                                fill=COL_ADIAB, width=2, dash=(4,4))

    # ── Work calculations ────────────────────────────────────────────────────
    def _update_work(self):
        p1, V1 = self.state1
        p2, V2 = self.state2
        dV = V2 - V1

        # isochoric: W_12 = 0 (no volume change on first leg)
        #            then isobaric at p2
        W_isochor = p2 * dV

        # isobaric at p1, then isochoric
        W_isobar = p1 * dV

        # isothermal: W = p1*V1 * ln(V2/V1)
        if V1 > 0 and V2 > 0 and V1 != V2:
            W_isotherm = p1 * V1 * math.log(V2 / V1)
        else:
            W_isotherm = 0.0

        # adiabatic: W = (p1*V1 - p2_ad*V2) / (γ-1)
        C = p1 * (V1 ** GAMMA)
        p2_ad = C / (V2 ** GAMMA) if V2 > 0 else p2
        W_adiab = (p1 * V1 - p2_ad * V2) / (GAMMA - 1)

        results = {
            "Isochor":     W_isochor,
            "Isobar":      W_isobar,
            "Isotherm":    W_isotherm,
            "Adiabatisch": W_adiab,
        }
        for name, W in results.items():
            sign = "+" if W >= 0 else ""
            self._work_labels[name].config(
                text=f"{sign}{W:.3f} J",
                fg=TEXT if abs(W) > 0.001 else TEXT_DIM)

    # ── Event handlers ───────────────────────────────────────────────────────
    def _on_click(self, event):
        V, p = self._c2w(event.x, event.y)
        V = max(V_MIN + 0.01, min(V_MAX - 0.01, V))
        p = max(P_MIN + 0.01, min(P_MAX - 0.01, p))

        if self.click_mode == 1:
            self.state1 = (p, V)
            self.state2 = None
            self.click_mode = 2
            self.s1_lbl.config(
                text=f"  p={p:.2f}   V={V:.2f}", fg=TEXT)
            self.s2_lbl.config(text="  nicht gesetzt", fg=TEXT_DIM)
            self.instr_lbl.config(
                text="② Klicke erneut\n   um Zustand 2 zu setzen")
            for lbl in self._work_labels.values():
                lbl.config(text="—", fg=TEXT_DIM)
        else:
            self.state2 = (p, V)
            self.click_mode = 1
            self.s2_lbl.config(
                text=f"  p={p:.2f}   V={V:.2f}", fg=TEXT)
            self.instr_lbl.config(
                text="① Klicke auf das Diagramm\n   um Zustand 1 zu setzen")

        self._redraw()

    def _on_hover(self, event):
        V, p = self._c2w(event.x, event.y)
        if V_MIN <= V <= V_MAX and P_MIN <= p <= P_MAX:
            self.coord_lbl.config(
                text=f"p = {p:.2f}   V = {V:.2f}", fg=TEXT_MID)
        else:
            self.coord_lbl.config(text="p = —   V = —", fg=TEXT_DIM)

    def _reset(self):
        self.state1 = None
        self.state2 = None
        self.click_mode = 1
        self.s1_lbl.config(text="  nicht gesetzt", fg=TEXT_DIM)
        self.s2_lbl.config(text="  nicht gesetzt", fg=TEXT_DIM)
        self.instr_lbl.config(
            text="① Klicke auf das Diagramm\n   um Zustand 1 zu setzen")
        for lbl in self._work_labels.values():
            lbl.config(text="—", fg=TEXT_DIM)
        self._redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = PVDiagram(root)
    root.mainloop()
