#!/usr/bin/env/python

"""
Simple plots for the recurrence model
"""

import numpy as np
import matplotlib.pyplot as plt
from hmtk.plotting.seismicity.catalogue_plots import \
        (get_completeness_adjusted_table, _save_image)
from openquake.hazardlib.mfd.truncated_gr import TruncatedGRMFD
from openquake.hazardlib.mfd.evenly_discretized import EvenlyDiscretizedMFD
from openquake.hazardlib.mfd.youngs_coppersmith_1985 import\
        YoungsCoppersmith1985MFD

def _check_recurrence_model_type(input_model):
    """

    """
    valid_model = False
    for model in [TruncatedGRMFD, EvenlyDiscretizedMFD,
            YoungsCoppersmith1985MFD]:
        valid_model = isinstance(input_model, model)
        if valid_model:
            break
    if not valid_model:
        raise ValueError('Recurrence model not recognised')

def _get_recurrence_model(input_model):
    """
    Returns the annual and cumulative recurrence rates predicted by the
    recurrence model
    """
    _check_recurrence_model_type(input_model)
    # Get model annual occurrence rates
    annual_rates = input_model.get_annual_occurrence_rates()
    annual_rates = np.array([[val[0], val[1]] for val in annual_rates])
    # Get cumulative rates
    cumulative_rates = np.array([np.sum(annual_rates[iloc:, 1])
                                 for iloc in range(0, len(annual_rates), 1)])
    return annual_rates, cumulative_rates

def _check_completeness_table(completeness, catalogue):
    """
    Generates the completeness table according to different instances
    """
    if isinstance(completeness, np.ndarray) and np.shape(completeness)[1] == 2:
        return completeness
    elif isinstance(completeness, float):
        return np.array([[float(np.min(catalogue.data['year'])),
                          completeness]])
    elif completeness is None:
        return np.array([[float(np.min(catalogue.data['year'])),
                          np.min(catalogue.data['magnitude'])]])
    else:
         raise ValueError('Completeness representation not recognised')


def plot_recurrence_model(input_model, catalogue, completeness, dmag,
        filename=None, filetype='png', dpi=300):
    """
    Plot a calculated recurrence model over an observed catalogue, adjusted for
    time-varying completeness
    """
    annual_rates, cumulative_rates = _get_recurrence_model(input_model)
    # Get observed annual recurrence
    if not catalogue.end_year:
        catalogue.update_end_year()
    obs_rates = get_completeness_adjusted_table(catalogue,
                                                completeness,
                                                input_model.bin_width,
                                                catalogue.end_year)
    # Create plot
    plt.semilogy(obs_rates[:, 0] + dmag / 2., obs_rates[:, 1], 'bo')
    plt.semilogy(annual_rates[:, 0], annual_rates[:, 1], 'b-')
    plt.semilogy(obs_rates[:, 0] + dmag / 2., obs_rates[:, 2], 'rs')
    plt.semilogy(annual_rates[:, 0], cumulative_rates, 'r-')
    plt.xlabel('Magnitude', fontsize='large')
    plt.ylabel('Annual Rate', fontsize='large')
    plt.legend(['Observed Incremental Rate',
                'Model Incremental Rate',
                'Observed Cumulative Rate',
                'Model Cumulative Rate'])
    _save_image(filename, filetype, dpi)

def plot_trunc_gr_model(aval, bval, min_mag, max_mag, dmag, catalogue=None,
        completeness=None, filename=None, filetype='png', dpi=300):
    """
    Plots a Gutenberg-Richter model
    """
    input_model = TruncatedGRMFD(min_mag, max_mag, dmag, aval, bval)
    if not catalogue:
        # Plot only the modelled recurrence
        annual_rates, cumulative_rates = _get_recurrence_model(input_model)
        plt.semilogy(annual_rates[:, 0], annual_rates[:, 1], 'b-')
        plt.semilogy(annual_rates[:, 0], cumulative_rates, 'r-')
        plt.xlabel('Magnitude', fontsize='large')
        plt.ylabel('Annual Rate', fontsize='large')
        plt.legend(['Incremental Rate', 'Cumulative Rate'])
        _save_image(filename, filetype, dpi)
    else:
        completeness = _check_completeness_table(completeness, catalogue)
        plot_recurrence_model(input_model,
                              catalogue,
                              completeness,
                              input_model.bin_width,
                              filename,
                              filetype,
                              dpi)
