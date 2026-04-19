from __future__ import annotations
import os
import math
import numpy as np
import scipy.linalg as LA
from sklearn import metrics
from sklearn.linear_model import Lasso, Ridge
from sklearn.preprocessing import PolynomialFeatures
from matplotlib.figure import Figure
import seaborn as sns
from .utils import AnalysisTools, AnalysisModes, RegularizationOptions, OperatorOptions, KoopmanAnalysisStatus, KoopmanAnalysisResponse

class Monomials(object):
    dim: int
    degree: int
    degrees: np.ndarray
    def __init__(self, dim: int, degree: int) -> None:
        super(Monomials, self).__init__()
        self.dim = dim
        self.degree = degree
        self.degrees = self._generate_degrees()

    def __len__(self) -> int:
        return self.degrees.shape[1]

    def lift(self, X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X[:, np.newaxis]
        X = X[:, np.newaxis, :]
        return np.prod(X ** self.degrees, axis=0)

    def diff(self, X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X[:, np.newaxis]
        P_diff = self.degrees - np.eye(self.dim)[:, np.newaxis, :]
        P_diff = np.maximum(P_diff, 0)
        terms = X[:, np.newaxis, np.newaxis, :] ** P_diff[..., np.newaxis]
        diff_monomials = np.prod(terms, axis=0)
        coeffs = self.degrees[:, :, 0].T[:, :, np.newaxis]
        valid_mask = (coeffs > 0)
        return coeffs * diff_monomials * valid_mask

    def ddiff(self, X: np.ndarray) -> np.ndarray:
        if X.ndim == 1:
            X = X[:, np.newaxis]
        P_exp = self.degrees[:, :, 0][:, :, np.newaxis, np.newaxis]
        I1 = np.eye(self.dim)[:, np.newaxis, :, np.newaxis]
        I2 = np.eye(self.dim)[:, np.newaxis, np.newaxis, :]
        P_ddiff = P_exp - I1 - I2
        P_ddiff = np.maximum(P_ddiff, 0)
        terms = X[:, np.newaxis, np.newaxis, np.newaxis, :] ** P_ddiff[..., np.newaxis]
        ddiff_monomials = np.prod(terms, axis=0)
        C1 = self.degrees[:, :, 0].T[:, :, np.newaxis]
        C2 = self.degrees[:, :, 0].T[:, np.newaxis, :]
        C2_adj = C2 - np.eye(self.dim)[np.newaxis, :, :]
        coeffs = C1 * C2_adj
        coeffs_exp = coeffs[:, :, :, np.newaxis]
        valid_mask = (coeffs_exp > 0)
        return coeffs_exp * ddiff_monomials * valid_mask

    def _generate_degrees(self) -> np.ndarray:
        poly = PolynomialFeatures(degree=self.degree, include_bias=True)
        dummy_X = np.zeros((1, self.dim))
        poly.fit(dummy_X)
        return poly.powers_.T[:, :, np.newaxis]

class EDMD(object):
    dim: int
    degree: int
    operator_option: OperatorOptions
    psi: Monomials
    K: np.ndarray | None
    data_range: tuple[float, float] | None
    def __init__(self, dim: int, degree: int, operator_option: OperatorOptions) -> None:
        super(EDMD, self).__init__()
        self.dim = dim
        self.degree = degree
        self.operator_option = operator_option
        self.psi = Monomials(dim=dim, degree=degree)
        self.K = None
        self.data_range = None

    def fit(self, X: np.ndarray, Y: np.ndarray, regularization_model: Lasso | Ridge | None = None, alpha: float | None = None) -> np.ndarray:
        self.data_range = (min(X.min(), Y.min()), max(X.max(), Y.max()))
        PsiX = self.psi.lift(X)
        PsiY = self.psi.lift(Y)
        if regularization_model is None:
            G = PsiX @ PsiX.T
            A = PsiX @ PsiY.T
            self.K = LA.pinv(G) @ A
        else:
            clf = regularization_model(alpha=alpha if alpha is not None else 1.0, fit_intercept=False, max_iter=1000)
            clf.fit(PsiX.T, PsiY.T)
            self.K = clf.coef_.T
        if self.operator_option == OperatorOptions.Left:
            self.K = self.K.conj().T
        return self.K

    def switch_operator(self, operator_option: OperatorOptions) -> None:
        if self.K is not None and self.operator_option != operator_option:
            self.K = self.K.conj().T
        self.operator_option = operator_option

class gEDMD(object):
    dim: int
    degree: int
    psi: Monomials
    dt: float
    operator_option: OperatorOptions
    L: np.ndarray | None
    data_range: tuple[float, float] | None
    def __init__(self, dim: int, degree: int, dt: float, operator_option: OperatorOptions) -> None:
        super(gEDMD, self).__init__()
        self.dim = dim
        self.degree = degree
        self.psi = Monomials(dim=dim, degree=degree)
        self.dt = dt
        self.operator_option = operator_option
        self.L = None
        self.data_range = None

    def fit(self, X: np.ndarray, Y: np.ndarray, regularization_model=None, alpha: float | None = None) -> np.ndarray:
        self.data_range = (min(X.min(), Y.min()), max(X.max(), Y.max()))
        dX = (Y - X) / self.dt
        PsiX = self.psi.lift(X)
        dPsiX = np.einsum('ijk,jk->ik', self.psi.diff(X), dX)
        if regularization_model is None:
            C_0 = PsiX @ PsiX.T
            C_1 = PsiX @ dPsiX.T
            self.L = LA.pinv(C_0) @ C_1
        else:
            clf = regularization_model(alpha=alpha if alpha is not None else 1.0, fit_intercept=False, max_iter=1000)
            clf.fit(PsiX.T, dPsiX.T)
            self.L = clf.coef_.T
        if self.operator_option == OperatorOptions.Left:
            self.L = self.L.conj().T
        return self.L

    def switch_operator(self, operator_option: OperatorOptions) -> None:
        if self.L is not None and self.operator_option != operator_option:
            self.L = self.L.conj().T
        self.operator_option = operator_option

class LogarithmicEDMD(EDMD):
    dt: float
    L: np.ndarray | None
    def __init__(self, dim: int, degree: int, dt: float, operator_option: OperatorOptions) -> None:
        super(LogarithmicEDMD, self).__init__(dim, degree, operator_option)
        self.dt = dt
        self.L = None

    def fit(self, X: np.ndarray, Y: np.ndarray, regularization_model=None, alpha: float | None = None) -> np.ndarray:
        self.K = super(LogarithmicEDMD, self).fit(X, Y, regularization_model, alpha)
        self.L = LA.logm(self.K) / self.dt
        return self.L

    def switch_operator(self, operator_option: OperatorOptions) -> None:
        if self.operator_option != operator_option:
            if self.K is not None:
                self.K = self.K.conj().T
            if self.L is not None:
                self.L = self.L.conj().T
        self.operator_option = operator_option

def create_matrix_figure(tool: EDMD | gEDMD | LogarithmicEDMD) -> Figure:
    figure = Figure(figsize=(5, 5))
    ax = figure.add_subplot(111)
    sns.heatmap(
        tool.K if type(tool) is EDMD else tool.L,
        annot=True,
        fmt='.2f',
        cmap='viridis',
        ax=ax
    )
    ax.set_title('Koopman Matrix' if type(tool) is EDMD else 'Koopman Generator')
    figure.tight_layout()
    return figure

def create_spectrum_figure(tool: EDMD | gEDMD | LogarithmicEDMD) -> Figure:
    figure = Figure(figsize=(5, 5))
    ax = figure.add_subplot(111)
    eigvals = LA.eigvals(tool.K if type(tool) is EDMD else tool.L)

    if type(tool) is EDMD:
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.plot(
            np.cos(theta),
            np.sin(theta),
            'k--',
            label='Unit Circle',
            alpha=0.5
        )
        ax.set_xlabel(r'Re($\lambda$)')
        ax.set_ylabel(r'Im($\lambda$)')
    else:
        ax.axvline(
            x=0,
            color='k',
            linestyle='--',
            label='Imaginary Axis',
            alpha=0.5
        )
        ax.set_xlabel(r'Re($\mu$)')
        ax.set_ylabel(r'Im($\mu$)')

    ax.scatter(
        eigvals.real,
        eigvals.imag,
        color='red',
        s=100,
        edgecolors='black',
        zorder=5,
        label='Eigenvalues'
    )
    ax.axhline(0, color='black', lw=0.5)
    if type(tool) is EDMD:
        ax.axvline(0, color='black', lw=0.5)
    max_val = max(np.max(np.abs(eigvals.real)), np.max(np.abs(eigvals.imag)))
    if type(tool) is EDMD:
        lim = max(1.1, max_val * 1.1)
    else:
        lim = max_val * 1.1 if max_val > 0 else 1.0
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.grid(True, linestyle=':')
    ax.set_title('Koopman Spectrum')
    ax.set_aspect('equal', adjustable='box')
    ax.legend()
    figure.tight_layout()
    return figure

def create_modes_figure(tool: EDMD | gEDMD | LogarithmicEDMD, index: int = 0) -> Figure:
    figure = Figure(figsize=(5, 5))
    ax = figure.add_subplot(111)
    _, eigvectors = LA.eig(tool.K if type(tool) is EDMD else tool.L)
    mode_magnitudes = np.abs(eigvectors[:, index])
    sns.barplot(
        x=range(len(mode_magnitudes)),
        y=mode_magnitudes,
        palette='viridis',
        hue=mode_magnitudes,
        ax=ax
    )
    ax.set_xlabel('Variable Index')
    ax.set_ylabel('Mode Magnitude')
    ax.set_title(f'Mode {index + 1} Magnitudes')
    figure.tight_layout()
    return figure

def create_eigenfunctions_figure(tool: EDMD | gEDMD | LogarithmicEDMD, index: int = 0) -> Figure:
    figure = Figure(figsize=(5, 5))
    ax = figure.add_subplot(111)
    _, left_eigvectors = LA.eig(tool.K if type(tool) is EDMD else tool.L, left=True, right=False)
    x = np.linspace(tool.data_range[0], tool.data_range[1], 100)
    y = np.linspace(tool.data_range[0], tool.data_range[1], 100)
    X, Y = np.meshgrid(x, y)
    X, Y = np.meshgrid(x, y)
    w = left_eigvectors[:, index].real
    Z = w[0] * X + w[1] * Y
    cp = ax.contourf(
        X, Y, Z,
        levels=50,
        cmap='viridis'
    )
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'Eigenfunction {index + 1}')
    figure.colorbar(cp, ax=ax)
    figure.tight_layout()
    return figure

def create_figure_from_analysis_mode(tool: EDMD | gEDMD | LogarithmicEDMD | None, analysis_mode: AnalysisModes, index: int = 0) -> Figure:
    if tool is None:
        return Figure()
    if analysis_mode == AnalysisModes.Matrix:
        return create_matrix_figure(tool)
    elif analysis_mode == AnalysisModes.Spectrum:
        return create_spectrum_figure(tool)
    elif analysis_mode == AnalysisModes.Modes:
        return create_modes_figure(tool, index)
    elif analysis_mode == AnalysisModes.Eigenfunctions:
        return create_eigenfunctions_figure(tool, index)
    else:
        return Figure()

def evaluate(tool: EDMD | gEDMD | LogarithmicEDMD, test_X: np.ndarray, test_Y: np.ndarray) -> dict[str, float]:
    if type(tool) is EDMD:
        test_PsiX = tool.psi.lift(test_X)
        test_PsiY = tool.psi.lift(test_Y)
        if tool.operator_option == OperatorOptions.Left:
            test_PsiY_pred = tool.K @ test_PsiX
        else:
            test_PsiY_pred = (test_PsiX.T @ tool.K).T
        inputs = test_PsiY
        targets = test_PsiY_pred
    else:
        test_PsiX = tool.psi.lift(test_X)
        test_dPsiX = np.einsum('ijk,jk->ik', tool.psi.diff(test_X), (test_Y - test_X) / tool.dt)
        if tool.operator_option == OperatorOptions.Left:
            test_dPsiX_pred = tool.L @ test_PsiX
        else:
            test_dPsiX_pred = (test_PsiX.T @ tool.L).T
        inputs = test_dPsiX
        targets = test_dPsiX_pred
    inputs = inputs.reshape(inputs.shape[0], -1).T
    targets = targets.reshape(targets.shape[0], -1).T
    rmse = metrics.root_mean_squared_error(inputs, targets)
    mae = metrics.mean_absolute_error(inputs, targets)
    re = np.linalg.norm(inputs - targets) / (np.linalg.norm(inputs) + 1e-8)
    r2 = metrics.r2_score(inputs, targets)
    return {
        'RMSE': rmse,
        'MAE': mae,
        'Relative Error': re,
        'R^2 Score': r2
    }

def koopman_analysis(
        tool,
        dim: int,
        degree: int,
        dt: float,
        train_ratio: float,
        regularization,
        alpha: float | None,
        operator_option,
        data_file: str,
        analysis_mode
) -> KoopmanAnalysisResponse:
    if not os.path.isfile(data_file):
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message=f'Error: File \'{data_file}\' not found.\n'
        )
    try:
        data = np.load(data_file)
        X = data['X']
        Y = data['Y']
    except Exception as e:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message=f'Error: Failed to load data from \'{data_file}\'.\n{str(e)}\n'
        )

    if X.shape != Y.shape:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message='Error: Shapes of X and Y do not match.\n '
        )

    if X.shape[0] != dim:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message=f'Error: Dimension of data ({X.shape[0]}) does not match specified dimension ({dim}).\n'
        )

    train_X = X[:, :int(X.shape[1] * train_ratio)]
    train_Y = Y[:, :int(Y.shape[1] * train_ratio)]
    test_X = X[:, int(X.shape[1] * train_ratio):]
    test_Y = Y[:, int(Y.shape[1] * train_ratio):]

    if regularization == RegularizationOptions.None_:
        regularization_model = None
    elif regularization == RegularizationOptions.Lasso:
        regularization_model = Lasso
    elif regularization == RegularizationOptions.Ridge:
        regularization_model = Ridge
    else:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message=f'Error: Invalid penalty option \'{regularization}\'.\n'
        )

    if tool == AnalysisTools.EDMD:
        tool = EDMD(
            dim=dim,
            degree=degree,
            operator_option=operator_option
        )
        tool.fit(
            train_X,
            train_Y,
            regularization_model=regularization_model,
            alpha=alpha
        )

    elif tool == AnalysisTools.gEDMD:
        tool = gEDMD(
            dim=dim,
            degree=degree,
            dt=dt,
            operator_option=operator_option
        )
        tool.fit(
            train_X,
            train_Y,
            regularization_model=regularization_model,
            alpha=alpha
        )

    elif tool == AnalysisTools.LogarithmicEDMD:
        tool = LogarithmicEDMD(
            dim=dim,
            degree=degree,
            dt=dt,
            operator_option=operator_option
        )
        tool.fit(
            train_X,
            train_Y,
            regularization_model=regularization_model,
            alpha=alpha
        )

    else:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Failure,
            message=f'Error: Invalid analysis tool \'{tool}\'.\n'
        )

    message = f'\nTraining Results:\n'
    train_evals = evaluate(tool, train_X, train_Y)
    metrics_max_length = max(len(metric) for metric in train_evals.keys())
    message += f'  - Data Number: {train_X.shape[1]}\n'
    message += f'  - Error      :\n'
    for metric, value in train_evals.items():
        message += f'    - {metric:>{metrics_max_length}}: {value:.4e}\n'

    if test_X.shape[1] == 0:
        return KoopmanAnalysisResponse(
            status=KoopmanAnalysisStatus.Success,
            message='\nNot enough test data for evaluation. Skipping evaluation step.\n\nKoopman analysis completed successfully.\n',
            figure=create_figure_from_analysis_mode(tool, analysis_mode),
            tool=tool
        )

    message += '\nTest Results:\n'
    test_evals = evaluate(tool, test_X, test_Y)
    metrics_max_length = max(len(metric) for metric in test_evals.keys())
    message += f'  - Data Number: {test_X.shape[1]}\n'
    message += f'  - Error      :\n'
    for metric, value in test_evals.items():
        message += f'    - {metric:>{metrics_max_length}}: {value:.4e}\n'

    return KoopmanAnalysisResponse(
        status=KoopmanAnalysisStatus.Success,
        message=f'{message}\nKoopman analysis completed successfully.\n',
        figure=create_figure_from_analysis_mode(tool, analysis_mode),
        tool=tool
    )