from __future__ import annotations
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as stext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from . import colors

class Sidebar(tk.Frame):
    width: int
    height: int
    def __init__(self, master: tk.Misc, width: int, height: int) -> None:
        super(Sidebar, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG,
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        pass

class Monitor(tk.Frame):
    width: int
    height: int
    textbox: stext.ScrolledText
    def __init__(self, master: tk.Misc, width: int, height: int) -> None:
        super(Monitor, self).__init__(
            master=master,
            width=width,
            height=height,
            bd=0,
            highlightthickness=0,
            bg=colors.MONITOR_BG
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkFixedFont').copy()
        font.config(size=max(10, int(self.master.winfo_screenheight() / 80)))
        self.textbox = stext.ScrolledText(
            master=self,
            width=self.width,
            height=self.height,
            bd=0,
            highlightthickness=0,
            fg=colors.MONITOR_FG,
            bg=colors.MONITOR_BG,
            font=font,
            state=tk.DISABLED
        )
        self.textbox.pack(fill=tk.BOTH, expand=True)

    def stdout(self, text: str) -> None:
        self.textbox.config(state=tk.NORMAL)
        self.textbox.insert(tk.END, f'{text}\n')
        self.textbox.see(tk.END)
        self.textbox.config(state=tk.DISABLED)

class Graph(tk.Frame):
    width: int
    height: int
    canvas: FigureCanvasTkAgg
    def __init__(self, master: tk.Misc, width: int, height: int) -> None:
        super(Graph, self).__init__(
            master=master,
            width=width,
            height=height,
            bd=0,
            highlightthickness=0,
            bg=colors.GRAPH_BG
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.canvas = FigureCanvasTkAgg(
            figure=Figure(
                figsize=(self.width / 100, self.height / 100),
                dpi=100,
                facecolor=colors.GRAPH_BG
            ),
            master=self
        )
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot(self, figure: Figure) -> None:
        self.canvas.get_tk_widget().destroy()
        figure.set_size_inches(self.width / figure.dpi, self.height / figure.dpi)
        self.canvas = FigureCanvasTkAgg(
            figure=figure,
            master=self
        )
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)