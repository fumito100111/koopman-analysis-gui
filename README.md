# Koopman Analysis GUI <!-- omit in toc -->

## Overview <!-- omit in toc -->

This application provides an intuitive GUI for executing and visualizing data-driven analysis based on the Koopman operator theory using `.npz` formatted datasets.
It supports analysis methods such as EDMD (Extended Dynamic Mode Decomposition), gEDMD and Logarithmic EDMD, allowing for a seamless workflow from adjusting various parameters to visualizing the matrix, spectrum, modes and eigenfunctions.

## Index <!-- omit in toc -->

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [How to launch the application](#how-to-launch-the-application)
  - [How to use the application](#how-to-use-the-application)
    - [Analysis Result details](#analysis-result-details)
    - [Matrix Visualization](#matrix-visualization)
    - [Spectrum Visualization](#spectrum-visualization)
    - [Modes Visualization](#modes-visualization)
    - [Eigenfunctions Visualization](#eigenfunctions-visualization)
    - [Other Options](#other-options)
- [References](#references)
- [Open Source Software](#open-source-software)
- [License](#license)

## Requirements

This software requires the following dependencies:

- Git
- Python 3.11 or higher

> [!NOTE]
> Internal analysis and rendering utilize packages such as `numpy`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `tkinter`, and `tkmacosx`.

## Installation

Run the following command in your terminal to install the application:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/fumito100111/koopman-analysis-gui/HEAD/install.sh)"
```

## Usage

### How to launch the application

After installation, you can launch the application by running the following command in your terminal:

```bash
kagui run
```

### How to use the application

After launching the application, you will see a GUI with various options for selecting the analysis method, adjusting parameters, loading datasets, and visualizing results.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/5d00f228-794d-41c8-9ddd-7397ff4f44ee">
</div>

1. **Select Analysis Method**: Choose the desired analysis method (EDMD, gEDMD, or Logarithmic EDMD) from the radio buttons.

2. **Adjust Parameters**: Use the sliders and input fields to adjust the parameters for the selected analysis method.
   If you use the gEDMD or Logarithmic EDMD method, you need to specify the time-step size ($\Delta t$) for the analysis.
   If you apply penalized regression, you need to select the regularization method and adjust the regularization parameter ($\alpha$).

3. **Select Dataset**: Click the `Select dataset` button to choose a `.npz` file containing the dataset you want to analyze.
   `.npz` files should contain the following arrays:
   - `X`: A 2D array of shape (n_features, n_samples) representing the state snapshots at time $t$.
   - `Y`: A 2D array of shape (n_features, n_samples) representing the state snapshots at time $t + 1$ or $t + \Delta t$.

4. **Select Analysis Modes**: Choose the analysis modes you want to visualize by selecting the radio buttons for `Matrix`, `Spectrum`, `Modes`, and `Eigenfunctions`.
   - `Matrix`: Visualize the Koopman operator (or generator) matrix.

   - `Spectrum`: Visualize the eigenvalues of the Koopman operator (or generator).
     If you use the EDMD method, the eigenvalues are in the discrete-time spectrum.
     If you use the gEDMD or Logarithmic EDMD method, the eigenvalues are transformed to the continuous-time spectrum.

   - `Modes`: Visualize the $i$-th Koopman mode.

   - `Eigenfunctions`: Visualize the $i$-th Koopman eigenfunction.

5. **Run Analysis**: Click the `Run Analysis` button to execute the analysis based on the selected method and parameters.
   The results will be displayed in the left panel of the GUI according to the selected analysis modes.
   The terminal at the bottom will show the log of the analysis, including the selected method, parameters, test evaluation metrics ($RMSE$, $MAE$, $Relative Error$, $R^2$), and any errors or warnings encountered during the analysis.

#### Analysis Result details

After running the analysis, the result details will be displayed in the terminal at the bottom of the GUI.
The details include the selected method, parameters, test evaluation metrics ($RMSE$, $MAE$, $Relative Error$, $R^2$), and any errors or warnings encountered during the analysis.

> [!IMPORTANT]
> If you set the train ratio to 1.0, the test evaluation metrics will not be calculated, and the terminal will show a warning message indicating that the test evaluation metrics are not available.

#### Matrix Visualization

The matrix visualization displays the Koopman operator (or generator) matrix as a heatmap.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/00197b67-2dda-4115-8c3c-247612b94145">
</div>

#### Spectrum Visualization

The spectrum visualization displays the eigenvalues of the Koopman operator (or generator) in the complex plane.

If you use the EDMD method, the eigenvalues are in the discrete-time spectrum, and the unit circle is highlighted to indicate stability.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/2b7aeaad-9f56-4e02-8213-99dd766ea8e4">
</div>

If you use the gEDMD or Logarithmic EDMD method, the eigenvalues are transformed to the continuous-time spectrum, and the imaginary axis is highlighted to indicate stability.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/95709b17-8aaf-4945-a020-131a9846012f">
</div>

#### Modes Visualization

The modes visualization displays the $i$-th Koopman mode as a bar plot.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/732de4bd-9180-4fbb-81db-fff83043b3b1">
</div>

You can change the selected mode index by using the `<` or `>` buttons.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/059a6a90-793b-41a2-8492-769c1f8c3b08">
</div>

#### Eigenfunctions Visualization

The eigenfunctions visualization displays the $i$-th Koopman eigenfunction as a contour plot.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/0d0d3fcb-f332-4b32-a700-b067ac9cea18">
</div>

You can change the selected eigenfunction index by using the `<` or `>` buttons.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/4fece881-84c2-4a30-8e42-a44ac592f6e6">
</div>

#### Other Options

You do not need to run the analysis again to change the operator options or the visualization modes.

If you want to switch between the left-hand and right-hand operators, you can change the `Operator Options` in the right panel of the GUI.

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/69c360dc-d5ed-4e5e-9076-ee7d9e4eb113">
</div>

If you want to change the analysis modes, you can switch the `Analysis Modes` in the right panel of the GUI.


## References

1. [A Data-Driven Approximation of the Koopman Operator: Extending Dynamic Mode Decomposition](https://link.springer.com/article/10.1007/s00332-015-9258-5)
2. [Data-driven approximation of the Koopman generator: Model reduction, system identification, and control](https://www.sciencedirect.com/science/article/pii/S0167278919306086?casa_token=Fk4ALPo811sAAAAA:LzIElkwDXXWdT5HhtMsIcL189wREBsJbzxA9bEmMVcpsvq0S9pFVa0SCLfkZgV5IBMDdk6K-iNI)
3. [Koopman-Based Lifting Techniques for Nonlinear Systems Identification](https://ieeexplore.ieee.org/abstract/document/8836606)

## Open Source Software

This project utilizes the following open-source software:

- [Python](https://www.python.org/)
- [NumPy](https://numpy.org/)
- [SciPy](https://www.scipy.org/)
- [scikit-learn](https://scikit-learn.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [tkmacosx](https://pypi.org/project/tkmacosx/)

## License

This project is licensed under the MIT License.
See the [`LICENSE`](LICENSE) file for details.