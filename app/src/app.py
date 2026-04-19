from __future__ import annotations
import tkinter as tk
from .widgets import Sidebar, Monitor, Graph

APP_NAME = 'Koopman Analysis GUI'

class App(tk.Tk):
    width: int
    height: int
    monitor: Monitor
    sidebar: Sidebar
    graph: Graph
    def __init__(self) -> None:
        super(App, self).__init__()
        self.title(APP_NAME)
        self.width = int(self.winfo_screenheight()*3 / 5) + int(self.winfo_screenwidth() / 4)
        self.height = int(self.winfo_screenheight()*3 / 5) + int(self.winfo_screenheight() / 5)
        self.geometry(
            f'{self.width}x{self.height}+{int((self.winfo_screenwidth() - self.width) / 2)}+{int((self.winfo_screenheight() - self.height) / 2)}'
        )
        self.resizable(False, False)
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        self.monitor = Monitor(
            master=self,
            width=self.width,
            height=int(self.winfo_screenheight() / 5),
        )
        self.monitor.place(
            relx=0.5,
            rely=1.0,
            anchor=tk.S
        )
        self.graph = Graph(
            master=self,
            width=int(self.winfo_screenheight() * 3 / 5),
            height=int(self.winfo_screenheight() * 3 / 5)
        )
        self.graph.place(
            relx=0.0,
            rely=0.0,
            anchor=tk.NW
        )
        self.sidebar = Sidebar(
            master=self,
            width=int(self.winfo_screenwidth() / 4),
            height=int(self.winfo_screenheight() * 3 / 5)
        )
        self.sidebar.place(
            relx=1.0,
            rely=0.0,
            anchor=tk.NE
        )

    def run(self) -> None:
        self.mainloop()