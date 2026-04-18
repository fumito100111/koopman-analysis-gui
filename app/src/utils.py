from __future__ import annotations
from typing import TYPE_CHECKING
import enum
import numpy as np
from matplotlib.figure import Figure
if TYPE_CHECKING:
    from .koopman import (
        EDMD, gEDMD, LogarithmicEDMD
    )

class AnalysisTools(enum.StrEnum):
    EDMD = 'EDMD'
    gEDMD = 'gEDMD'
    LogarithmicEDMD = 'Logarithmic EDMD'

class AnalysisModes(enum.StrEnum):
    Matrix = 'Matrix'
    Spectrum = 'Spectrum'
    Modes = 'Modes'
    Eigenfunctions = 'Eigenfunctions'

class Parameters(enum.StrEnum):
    dim = 'Dimension'
    degree = 'Degree'
    dt = 'Time Step'
    train_ratio = 'Train Ratio',
    alpha = 'Alpha'

class RegularizationOptions(enum.StrEnum):
    None_ = 'None'
    Lasso = 'Lasso'
    Ridge = 'Ridge'

class OperatorOptions(enum.StrEnum):
    Left = 'Left'
    Right = 'Right'

class KoopmanAnalysisStatus(enum.StrEnum):
    Success = enum.auto()
    Failure = enum.auto()

class KoopmanAnalysisResponse(object):
    status: KoopmanAnalysisStatus
    message: str | None
    figure: Figure | None
    tool: EDMD | gEDMD | LogarithmicEDMD | None
    def __init__(
        self,
        status: KoopmanAnalysisStatus = KoopmanAnalysisStatus.Success,
        message: str | None = None,
        figure: Figure | None = None,
        tool: EDMD | gEDMD | LogarithmicEDMD | None = None
    ) -> None:
        self.status = status
        self.message = message
        self.figure = figure
        self.tool = tool

PARAMETERS_NAME_MAX_LENGTH = max(len(parameter.value) for parameter in Parameters)
PARAMETER_MAX_LENGTH = 5
FILENAME_SHOW_MAX_LENGTH = 20