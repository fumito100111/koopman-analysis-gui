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

PARAMETERS_NAME_MAX_LENGTH = max(len(parameter.value) for parameter in Parameters)
PARAMETER_MAX_LENGTH = 5