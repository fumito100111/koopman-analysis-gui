from __future__ import annotations
from typing import TYPE_CHECKING, Callable
import sys
import math
import tkinter as tk
import tkinter.font as tkfont
import tkinter.filedialog as tkfd
import tkinter.scrolledtext as stext
import tkmacosx as mactk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .utils import (
    AnalysisTools,
    AnalysisModes,
    Parameters,
    PARAMETERS_NAME_MAX_LENGTH,
    PARAMETER_MAX_LENGTH,
    OperatorOptions,
    FILENAME_SHOW_MAX_LENGTH
)
from . import colors
if TYPE_CHECKING:
    from .app import App

class RadioButton(tk.Frame):
    width: int
    height: int
    text: str
    value: str
    variable: tk.Variable
    radio_button: tk.Radiobutton
    def __init__(self, master: AnalysisToolsPanel, width: int, height: int, text: str, value: str, variable: tk.Variable, command: Callable[[], None] | None = None) -> None:
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
        tk.Label(
            master=self,
            text=self.text,
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).pack(side=tk.TOP)
        self.radio_button = tk.Radiobutton(
            master=self,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG,
            value=self.value,
            variable=self.variable,
            command=self.command
        )
        self.radio_button.pack(side=tk.TOP)

class AnalysisToolsPanel(tk.Frame):
    width: int
    height: int
    previous_tool: AnalysisTools
    selected_tool: tk.StringVar
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(AnalysisToolsPanel, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.previous_tool = None
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        tk.Label(
            master=self,
            text='Analysis Tools',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.02, rely=0.0, anchor=tk.NW)
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
                command=lambda t=tool: self.set_tool(t)
            ).place(relx=i / len(AnalysisTools), rely=0.3, anchor=tk.NW)
        self.selected_tool.set(AnalysisTools.EDMD.value)
        self.set_tool(AnalysisTools.EDMD)

    def set_tool(self, tool: AnalysisTools) -> None:
        if self.previous_tool == tool:
            return
        if tool == AnalysisTools.EDMD:
            self.set_edmd()
        elif tool == AnalysisTools.gEDMD:
            self.set_gedmd()
        elif tool == AnalysisTools.LogarithmicEDMD:
            self.set_logarithmic_edmd()
        self.previous_tool = tool

    def set_edmd(self) -> None:
        print('Selected EDMD')
        pass

    def set_gedmd(self) -> None:
        print('Selected gEDMD')
        pass

    def set_logarithmic_edmd(self) -> None:
        print('Selected Logarithmic EDMD')
        pass

class ParameterField(tk.Frame):
    width: int
    height: int
    field: tk.Entry
    def __init__(self, master: ParametersPanel, width: int, height: int, text: str) -> None:
        super(ParameterField, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.text = text
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(10, int(self.master.winfo_screenheight() / 70)))
        tk.Label(
            master=self,
            text=self.text,
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG,
            width=PARAMETERS_NAME_MAX_LENGTH,
            anchor=tk.E
        ).pack(side=tk.LEFT)
        self.field = tk.Entry(
            master=self,
            width=PARAMETER_MAX_LENGTH,
            font=font,
            fg=colors.PARAMETER_FIELD_FG,
            bg=colors.PARAMETER_FIELD_BG,
            highlightthickness=1,
            highlightbackground=colors.PARAMETER_FIELD_DEACTIVE_BORDER,
            highlightcolor=colors.PARAMETER_FIELD_ACTIVE_BORDER
        )
        self.field.pack(side=tk.RIGHT)

class ParametersPanel(tk.Frame):
    width: int
    height: int
    fields: dict[Parameters, ParameterField]
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(ParametersPanel, self).__init__(
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
        self.fields[Parameters.train_ratio].field.insert(0, '0.8')

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        tk.Label(
            master=self,
            text='Parameters',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.02, rely=0.0, anchor=tk.NW)
        self.fields = {}
        self.fields[Parameters.dim] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{' ' * max(0, PARAMETERS_NAME_MAX_LENGTH - len(Parameters.dim.value))}{Parameters.dim.value} : '
        )
        self.fields[Parameters.dim].place(relx=0.01, rely=0.45, anchor=tk.W)
        self.fields[Parameters.degree] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{' ' * max(0, PARAMETERS_NAME_MAX_LENGTH - len(Parameters.degree.value))}{Parameters.degree.value} : '
        )
        self.fields[Parameters.degree].place(relx=0.01, rely=0.85, anchor=tk.W)
        self.fields[Parameters.dt] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{' ' * max(0, PARAMETERS_NAME_MAX_LENGTH - len(Parameters.dt.value))}{Parameters.dt.value} : '
        )
        self.fields[Parameters.dt].place(relx=0.9, rely=0.45, anchor=tk.E)
        self.fields[Parameters.train_ratio] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{' ' * max(0, PARAMETERS_NAME_MAX_LENGTH - len(Parameters.train_ratio.value))}{Parameters.train_ratio.value} : '
        )
        self.fields[Parameters.train_ratio].place(relx=0.9, rely=0.85, anchor=tk.E)

    def get_parameters(self) -> dict[Parameters, int | float | None]:
        return {
            Parameters.dim: self.get_dim(),
            Parameters.degree: self.get_degree(),
            Parameters.dt: self.get_dt(),
            Parameters.train_ratio: self.get_train_ratio()
        }

    def get_dim(self) -> int | None:
        try:
            dim = int(self.fields[Parameters.dim].field.get())
            return dim if dim > 0 else None
        except ValueError:
            return None

    def get_degree(self) -> int | None:
        try:
            degree = int(self.fields[Parameters.degree].field.get())
            return degree if degree > 0 else None
        except ValueError:
            return None

    def get_dt(self) -> float | None:
        try:
            dt = float(self.fields[Parameters.dt].field.get())
            return dt if dt > 0.0 else None
        except ValueError:
            return None

    def get_train_ratio(self) -> float | None:
        try:
            train_ratio = float(self.fields[Parameters.train_ratio].field.get())
            return train_ratio if 0.0 < train_ratio <= 1.0 else None
        except ValueError:
            return None

class OperatorOptionsPanel(tk.Frame):
    width: int
    height: int
    previous_option: OperatorOptions
    selected_option: tk.StringVar
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(OperatorOptionsPanel, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.previous_option = None
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        tk.Label(
            master=self,
            text='Operator Options',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.02, rely=0.0, anchor=tk.NW)
        self.selected_option = tk.StringVar()
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(10, int(self.master.winfo_screenheight() / 70)))
        tk.Radiobutton(
            master=self,
            text=OperatorOptions.Left.value,
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG,
            value=OperatorOptions.Left.value,
            variable=self.selected_option,
            command=lambda o=OperatorOptions.Left: self.set_option(o)
        ).place(relx=0.25, rely=0.5, anchor=tk.NW)
        tk.Radiobutton(
            master=self,
            text=OperatorOptions.Right.value,
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG,
            value=OperatorOptions.Right.value,
            variable=self.selected_option,
            command=lambda o=OperatorOptions.Right: self.set_option(o)
        ).place(relx=0.75, rely=0.5, anchor=tk.NE)
        self.selected_option.set(OperatorOptions.Left.value)
        self.set_option(OperatorOptions.Left)

    def set_option(self, option: OperatorOptions) -> None:
        if self.previous_option == option:
            return
        if option == OperatorOptions.Left:
            self.set_left()
        elif option == OperatorOptions.Right:
            self.set_right()
        self.previous_option = option

    def set_left(self) -> None:
        print('Selected Left operator')
        pass

    def set_right(self) -> None:
        print('Selected Right operator')
        pass

class DatasetPanel(tk.Frame):
    width: int
    height: int
    selected_file: str
    file_dialog_button: tk.Button | mactk.Button
    label: tk.Label
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(DatasetPanel, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.selected_file = ''
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        tk.Label(
            master=self,
            text='Dataset',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.02, rely=0.0, anchor=tk.NW)
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(8, int(self.master.winfo_screenheight() / 80)))
        button_kwargs = {
            'master': self,
            'text': 'Select dataset',
            'font': font,
            'fg': colors.FILEDIALOG_BUTTON_FG,
            'bg': colors.FILEDIALOG_BUTTON_BG,
            'activeforeground': colors.FILEDIALOG_BUTTON_ACTIVE_FG,
            'activebackground': colors.FILEDIALOG_BUTTON_ACTIVE_BG,
            'bordercolor': colors.FILEDIALOG_BUTTON_BORDER,
            'highlightthickness': 1,
            'command': self.select_dataset
        }
        if sys.platform == 'darwin':
            self.file_dialog_button = mactk.Button(**button_kwargs, borderless=True)
        else:
            self.file_dialog_button = tk.Button(**button_kwargs)
        self.file_dialog_button.place(relx=0.05, rely=0.6, anchor=tk.W)
        self.label = tk.Label(
            master=self,
            text='No dataset selected',
            font=font,
            fg=colors.FILENAME_LABEL_FG,
            bg=colors.FILENAME_LABEL_BG,
            width=FILENAME_SHOW_MAX_LENGTH
        )
        self.label.place(relx=0.95, rely=0.6, anchor=tk.E)

    def select_dataset(self, event: tk.Event | None = None) -> None:
        file = tkfd.askopenfilename(
            title='Select dataset',
            filetypes=[
                ('Numpy Zip files', '*.npz')
            ]
        )
        if file:
            self.selected_file = file
            if len(file) > FILENAME_SHOW_MAX_LENGTH:
                prefix = '.../'
                filename = file.split('/')[-1]
                filename = f'{prefix}{filename[-(FILENAME_SHOW_MAX_LENGTH - len(prefix)):]}'
            else:
                filename = file
            self.label.config(text=filename)

class AnalysisModesPanel(tk.Frame):
    width: int
    height: int
    previous_mode: AnalysisModes
    selected_mode: tk.StringVar
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(AnalysisModesPanel, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.previous_mode = None
        self.initialize()

    def initialize(self) -> None:
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(12, int(self.master.winfo_screenheight() / 60)), weight=tkfont.BOLD)
        tk.Label(
            master=self,
            text='Analysis Modes',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.02, rely=0.0, anchor=tk.NW)
        self.selected_mode = tk.StringVar()
        for i, mode in enumerate(AnalysisModes):
            text = mode.value
            font = tkfont.nametofont('TkDefaultFont').copy()
            font.config(size=max(10, int(self.master.winfo_screenheight() / 70)))
            tk.Radiobutton(
                master=self,
                text=text,
                font=font,
                fg=colors.SIDEBAR_FG,
                bg=colors.SIDEBAR_BG,
                value=mode.value,
                variable=self.selected_mode,
                command=lambda m=mode: self.set_mode(m)
            ).place(relx=(i // 2) * (1 / (len(AnalysisModes) // 2)) + 0.1, rely=0.35 * (i % 2 + 1), anchor=tk.NW)
        self.selected_mode.set(AnalysisModes.Matrix.value)
        self.set_mode(AnalysisModes.Matrix)

    def set_mode(self, mode: AnalysisModes) -> None:
        if self.previous_mode == mode:
            return
        if mode == AnalysisModes.Matrix:
            self.set_matrix()
        elif mode == AnalysisModes.Spectrum:
            self.set_spectrum()
        elif mode == AnalysisModes.Modes:
            self.set_modes()
        elif mode == AnalysisModes.Eigenfunctions:
            self.set_eigenfunctions()
        self.previous_mode = mode

    def set_matrix(self) -> None:
        print('Selected Matrix mode')
        pass

    def set_spectrum(self) -> None:
        print('Selected Spectrum mode')
        pass

    def set_modes(self) -> None:
        print('Selected Modes mode')
        pass

    def set_eigenfunctions(self) -> None:
        print('Selected Eigenfunctions mode')
        pass

class AnalysisButton(tk.Frame):
    width: int
    height: int
    button: tk.Button | mactk.Button
    def __init__(self, master: Sidebar, width: int, height: int) -> None:
        super(AnalysisButton, self).__init__(
            master=master,
            width=width,
            height=height,
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        font = tkfont.nametofont('TkDefaultFont').copy()
        font.config(size=max(14, int(self.master.winfo_screenheight() / 50)), weight=tkfont.BOLD)
        button_kwargs = {
            'master': self,
            'text': 'Run Analysis',
            'font': font,
            'fg': colors.ANALYSIS_BUTTON_FG,
            'bg': colors.ANALYSIS_BUTTON_BG,
            'activeforeground': colors.ANALYSIS_BUTTON_ACTIVE_FG,
            'activebackground': colors.ANALYSIS_BUTTON_ACTIVE_BG,
            'command': self.analyze
        }
        if sys.platform == 'darwin':
            self.button = mactk.Button(**button_kwargs, borderless=True)
        else:
            self.button = tk.Button(**button_kwargs)
        self.button.pack(fill=tk.BOTH, expand=True)

    def analyze(self, event: tk.Event | None = None) -> None:
        print('Analyzing...')
        print(f'Selected Tool: {self.master.analysis_tools_panel.selected_tool.get()}')
        print(f'Parameters: {self.master.parameters_panel.get_parameters()}')
        pass

class Sidebar(tk.Frame):
    width: int
    height: int
    analysis_tools_panel: AnalysisToolsPanel
    parameters_panel: ParametersPanel
    operator_options_panel: OperatorOptionsPanel
    dataset_panel: DatasetPanel
    analysis_modes_panel: AnalysisModesPanel
    analysis_button: AnalysisButton
    def __init__(self, master: App, width: int, height: int) -> None:
        super(Sidebar, self).__init__(
            master=master,
            width=width,
            height=height,
            # bg=colors.SIDEBAR_BG
            bg='lightblue'
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        self.analysis_tools_panel = AnalysisToolsPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.15)
        )
        self.analysis_tools_panel.place(relx=0.0, rely=0.01, anchor=tk.NW)
        self.parameters_panel = ParametersPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.3)
        )
        self.parameters_panel.place(relx=0.0, rely=0.17, anchor=tk.NW)
        self.operator_options_panel = OperatorOptionsPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.09)
        )
        self.operator_options_panel.place(relx=0.0, rely=0.48, anchor=tk.NW)
        self.dataset_panel = DatasetPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.15)
        )
        self.dataset_panel.place(relx=0.0, rely=0.58, anchor=tk.NW)
        self.analysis_modes_panel = AnalysisModesPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.15)
        )
        self.analysis_modes_panel.place(relx=0.0, rely=0.74, anchor=tk.NW)
        self.analysis_button = AnalysisButton(
            master=self,
            width=self.width,
            height=int(self.height * 0.1)
        )
        self.analysis_button.place(relx=0.5, rely=1.0, anchor=tk.S)

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