from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import tkinter as tk
import tkinter.font as tkfont
import tkinter.scrolledtext as stext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .utils import AnalysisTools
from . import colors
if TYPE_CHECKING:
    from .app import App

class RadioButton(tk.Frame):
    width: int
    height: int
    text: str
    value: str
    variable: tk.Variable
    label: tk.Label
    radio_button: tk.Radiobutton
    def __init__(self, master: tk.Misc, width: int, height: int, text: str, value: str, variable: tk.Variable, command: Callable[[], None] | None = None) -> None:
        super(RadioButton, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.text = text
        self.value = value
        self.variable = variable
        self.command = command
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(10, int(self.master.winfo_screenheight() / 70)))
        self.label = tk.Label(
            master=self,
            text=self.text,
            font=font,
            bg=colors.SIDEBAR_BG,
            fg=colors.SIDEBAR_FG
        )
        self.label.pack(side=tk.TOP)
        self.radio_button = tk.Radiobutton(
            master=self,
            bg=colors.SIDEBAR_BG,
            fg=colors.SIDEBAR_FG,
            value=self.value,
            variable=self.variable,
            command=self.command
        )
        self.radio_button.pack(side=tk.TOP)

class AnalysisToolsPanel(tk.Frame):
    width: int
    height: int
    selected_tool: tk.StringVar
    def __init__(self, master: tk.Misc, width: int, height: int) -> None:
        super(AnalysisToolsPanel, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        self.label = tk.Label(
            master=self,
            text='Analysis Tools',
            font=font,
            bg=colors.SIDEBAR_BG,
            fg=colors.SIDEBAR_FG
        )
        self.label.place(relx=0.0, rely=0.0, anchor=tk.NW)
        self.selected_tool = tk.StringVar()
        for i, tool in enumerate(AnalysisTools):
            text = tool.value.replace(' ', '\n')
            if tool != AnalysisTools.LogarithmicEDMD:
                text = f'\n{text}'
            RadioButton(
                master=self,
                width=int(self.width / len(AnalysisTools)),
                height=int(self.height * 0.7),
                text=text,
                value=tool.value,
                variable=self.selected_tool,
                command=lambda t=tool: print(f'Selected tool: {t.value}')
            ).place(relx=i / len(AnalysisTools), rely=0.3, anchor=tk.NW)
        self.selected_tool.set(AnalysisTools.EDMD.value)

class Sidebar(tk.Frame):
    width: int
    height: int
    def __init__(self, master: App, width: int, height: int) -> None:
        super(Sidebar, self).__init__(
            master=master,
            width=width,
            height=height,
            # bg=colors.SIDEBAR_BG,
            bg='lightblue'
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        AnalysisToolsPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.15)
        ).place(relx=0.0, rely=0.01, anchor=tk.NW)



class Monitor(tk.Frame):
    width: int
    height: int
    textbox: stext.ScrolledText
    def __init__(self, master: App, width: int, height: int) -> None:
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
    def __init__(self, master: App, width: int, height: int) -> None:
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