from __future__ import annotations
import enum

class AnalysisTools(enum.StrEnum):
    EDMD = 'EDMD'
    gEDMD = 'gEDMD'
    LogarithmicEDMD = 'Logarithmic EDMD'

class Parameters(enum.StrEnum):
    dim = 'Dimension'
    degree = 'Degree'
    dt = 'Time Step'
    train_ratio = 'Train Ratio'

PARAMETERS_NAME_MAX_LENGTH = max(len(parameter.value) for parameter in Parameters)
PARAMETER_MAX_LENGTH = 5

FILENAME_SHOW_MAX_LENGTH = 25