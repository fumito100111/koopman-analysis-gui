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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from .utils import (
    AnalysisTools,
    AnalysisModes,
    Parameters,
    PARAMETERS_NAME_MAX_LENGTH,
    PARAMETER_MAX_LENGTH,
    RegularizationOptions,
    OperatorOptions,
    KoopmanAnalysisStatus,
    FILENAME_SHOW_MAX_LENGTH
)
from .koopman import EDMD, gEDMD, LogarithmicEDMD, koopman_analysis, create_figure_from_analysis_mode
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
        self.master.parameters_panel.fields[Parameters.dt].field.config(state=tk.DISABLED)

    def set_gedmd(self) -> None:
        self.master.parameters_panel.fields[Parameters.dt].field.config(state=tk.NORMAL)

    def set_logarithmic_edmd(self) -> None:
        self.master.parameters_panel.fields[Parameters.dt].field.config(state=tk.NORMAL)

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
    regularization_panel: RegularizationOptionsSubPanel
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
            text=f'{Parameters.dim.value} : '
        )
        self.fields[Parameters.dim].place(relx=0.01, rely=0.25, anchor=tk.W)
        self.fields[Parameters.degree] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{Parameters.degree.value} : '
        )
        self.fields[Parameters.degree].place(relx=0.01, rely=0.5, anchor=tk.W)
        self.fields[Parameters.dt] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{Parameters.dt.value} : '
        )
        self.fields[Parameters.dt].place(relx=0.9, rely=0.25, anchor=tk.E)
        self.fields[Parameters.dt].field.config(
            disabledforeground=colors.PARAMETER_FIELD_DISABLED_FG,
            disabledbackground=colors.PARAMETER_FIELD_DISABLED_BG
        )
        self.fields[Parameters.train_ratio] = ParameterField(
            master=self,
            width=self.width,
            height=int(self.height / len(Parameters)),
            text=f'{Parameters.train_ratio.value} : '
        )
        self.fields[Parameters.train_ratio].place(relx=0.9, rely=0.5, anchor=tk.E)

        self.regularization_panel = RegularizationOptionsSubPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.4)
        )
        self.regularization_panel.place(relx=0.0, rely=0.6, anchor=tk.NW)

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

class RegularizationOptionsSubPanel(tk.Frame):
    width: int
    height: int
    alpha_field: ParameterField
    previous_option: RegularizationOptions
    selected_option: tk.StringVar
    def __init__(self, master: ParametersPanel, width: int, height: int) -> None:
        super(RegularizationOptionsSubPanel, self).__init__(
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
        font.config(size=max(10, int(self.master.winfo_screenheight() / 70)))
        tk.Label(
            master=self,
            text='Regularization : ',
            font=font,
            fg=colors.SIDEBAR_FG,
            bg=colors.SIDEBAR_BG
        ).place(relx=0.05, rely=0.5, anchor=tk.W)
        self.selected_option = tk.StringVar()
        for i, option in enumerate(RegularizationOptions):
            text = option.value
            tk.Radiobutton(
                master=self,
                text=text,
                font=font,
                fg=colors.SIDEBAR_FG,
                bg=colors.SIDEBAR_BG,
                value=option.value,
                variable=self.selected_option,
                command=lambda o=option: self.set_option(o)
            ).place(relx=0.35, rely=0.5 + (i - 1) * 0.3, anchor=tk.W)
        self.alpha_field = ParameterField(
            master=self,
            width=int(self.width * 0.3),
            height=int(self.height * 0.4),
            text=f'{Parameters.alpha.value} : '
        )
        self.alpha_field.place(relx=0.9, rely=0.5, anchor=tk.E)
        self.alpha_field.lower()
        self.alpha_field.field.config(
            disabledforeground=colors.PARAMETER_FIELD_DISABLED_FG,
            disabledbackground=colors.PARAMETER_FIELD_DISABLED_BG
        )
        self.alpha_field.field.insert(0, '1.0')
        self.alpha_field.field.config(state=tk.DISABLED)
        self.selected_option.set(RegularizationOptions.None_.value)
        self.set_option(RegularizationOptions.None_)

    def set_option(self, option: RegularizationOptions) -> None:
        if self.previous_option == option:
            return
        if option == RegularizationOptions.None_:
            self.set_none()
        elif option == RegularizationOptions.Lasso:
            self.set_lasso()
        elif option == RegularizationOptions.Ridge:
            self.set_ridge()
        self.previous_option = option

    def set_none(self) -> None:
        self.alpha_field.field.config(state=tk.DISABLED)

    def set_lasso(self) -> None:
        self.alpha_field.field.config(state=tk.NORMAL)

    def set_ridge(self) -> None:
        self.alpha_field.field.config(state=tk.NORMAL)

    def get_alpha(self) -> float | None:
        try:
            alpha = float(self.alpha_field.field.get())
            return alpha if alpha > 0.0 else None
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
        if self.master.master.graph.tool is not None:
            self.master.master.graph.tool.switch_operator(OperatorOptions.Left)
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, self.master.analysis_modes_panel.selected_mode.get())
            self.master.master.graph.plot(figure)

    def set_right(self) -> None:
        if self.master.master.graph.tool is not None:
            self.master.master.graph.tool.switch_operator(OperatorOptions.Right)
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, self.master.analysis_modes_panel.selected_mode.get())
            self.master.master.graph.plot(figure)

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
        if self.master.master.graph.tool is not None:
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, AnalysisModes.Matrix)
            self.master.master.graph.plot(figure)

    def set_spectrum(self) -> None:
        if self.master.master.graph.tool is not None:
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, AnalysisModes.Spectrum)
            self.master.master.graph.plot(figure)

    def set_modes(self) -> None:
        if self.master.master.graph.tool is not None:
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, AnalysisModes.Modes)
            self.master.master.graph.plot(figure)

    def set_eigenfunctions(self) -> None:
        if self.master.master.graph.tool is not None:
            figure = create_figure_from_analysis_mode(self.master.master.graph.tool, AnalysisModes.Eigenfunctions)
            self.master.master.graph.plot(figure)

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
        tool = self.master.analysis_tools_panel.selected_tool.get()
        dim = self.master.parameters_panel.get_dim()
        if dim is None:
            self.master.master.monitor.stdout('Invalid dimension. Please enter a positive integer.')
            return
        degree = self.master.parameters_panel.get_degree()
        if degree is None:
            self.master.master.monitor.stdout('Invalid degree. Please enter a positive integer.')
            return
        dt = self.master.parameters_panel.get_dt()
        if dt is None and tool != AnalysisTools.EDMD.value:
            self.master.master.monitor.stdout('Invalid time step. Please enter a positive number.')
            return
        train_ratio = self.master.parameters_panel.get_train_ratio()
        if train_ratio is None:
            self.master.master.monitor.stdout('Invalid train ratio. Please enter a value where 0.0 < ratio <= 1.0.')
            return
        regularization = self.master.parameters_panel.regularization_panel.selected_option.get()
        alpha = self.master.parameters_panel.regularization_panel.get_alpha() if regularization != RegularizationOptions.None_.value else None
        if regularization != RegularizationOptions.None_.value and alpha is None:
            self.master.master.monitor.stdout('Invalid alpha. Please enter a positive number.')
            return
        operator_option = self.master.operator_options_panel.selected_option.get()
        data_file = self.master.dataset_panel.selected_file
        if not data_file:
            self.master.master.monitor.stdout('No dataset selected. Please select a dataset.')
            return
        analysis_mode = self.master.analysis_modes_panel.selected_mode.get()
        self.master.master.monitor.stdout(f'Running analysis with the following settings:')
        self.master.master.monitor.stdout(f'  - Analysis Tool : {tool}')
        self.master.master.monitor.stdout(f'  - Parameters')
        self.master.master.monitor.stdout(f'    - Dimension        : {dim}')
        self.master.master.monitor.stdout(f'    - Degree           : {degree}')
        self.master.master.monitor.stdout(f'    - Time step        : {dt}')
        self.master.master.monitor.stdout(f'    - Train ratio      : {train_ratio}')
        self.master.master.monitor.stdout(f'    - Regularization   : {regularization}' + (f' (alpha: {alpha})' if regularization != RegularizationOptions.None_.value else ''))
        self.master.master.monitor.stdout(f'    - Operator Options : {operator_option}')
        self.master.master.monitor.stdout(f'  - Dataset : {data_file}')
        self.master.master.monitor.stdout(f'  - Analysis Mode : {analysis_mode}')

        response = koopman_analysis(
            tool=tool,
            dim=dim,
            degree=degree,
            dt=dt,
            train_ratio=train_ratio,
            regularization=regularization,
            alpha=alpha,
            operator_option=operator_option,
            data_file=data_file,
            analysis_mode=analysis_mode
        )

        if response.status == KoopmanAnalysisStatus.Success:
            self.master.master.monitor.stdout(response.message)
            self.master.master.graph.plot(response.figure)
            self.master.master.graph.tool = response.tool
        else:
            self.master.master.monitor.stdout('Koopman analysis failed.')
            self.master.master.monitor.stdout(f'Error: {response.message}')

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
            bg=colors.SIDEBAR_BG
        )
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self) -> None:
        self.pack_propagate(False)
        self.layout()

    def layout(self) -> None:
        self.parameters_panel = ParametersPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.3)
        )
        self.parameters_panel.place(relx=0.0, rely=0.17, anchor=tk.NW)
        self.analysis_tools_panel = AnalysisToolsPanel(
            master=self,
            width=self.width,
            height=int(self.height * 0.15)
        )
        self.analysis_tools_panel.place(relx=0.0, rely=0.01, anchor=tk.NW)
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
    toolbar: NavigationToolbar2Tk
    tool: EDMD | gEDMD | LogarithmicEDMD | None
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
        self.tool = None
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
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.place(relx=0.99, rely=0.99, anchor=tk.SE)

    def plot(self, figure: Figure) -> None:
        self.canvas.get_tk_widget().destroy()
        self.toolbar.destroy()
        figure.set_size_inches(self.width / figure.dpi, self.height / figure.dpi)
        self.canvas = FigureCanvasTkAgg(
            figure=figure,
            master=self
        )
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.place(relx=0.99, rely=0.99, anchor=tk.SE)