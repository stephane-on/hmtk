#!/usr/bin/env/python

"""
Collection of tools for plotting descriptive statistics of a catalogue
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from math import log10

# Default the figure size
DEFAULT_SIZE = (8., 6.)


def build_filename(filename, filetype='png', resolution=300):
    """
    Uses the input properties to create the string of the filename
    :param str filename:
        Name of the file
    :param str filetype:
        Type of file
    :param int resolution:
        DPI resolution of the output figure
    """
    filevals = os.path.splitext(filename)
    if filevals[1]:
        filetype = filevals[1][1:]
    if not filetype:
        filetype = 'png'

    filename = filevals[0] + '.' + filetype

    if not resolution:
        resolution = 300
    return filename, filetype, resolution

def _save_image(filename, filetype='png', resolution=300):
    """
    If filename is specified, saves the image
    :param str filename:
        Name of the file
    :param str filetype:
        Type of file
    :param int resolution:
        DPI resolution of the output figure
    """
    if filename:
        filename, filetype, resolution = build_filename(filename,
                                                        filetype,
                                                        resolution)
        plt.savefig(filename, dpi=resolution, format=filetype)
    else:
        pass
    return

def _get_catalogue_bin_limits(catalogue, dmag):
    """
    Returns the magnitude bins corresponing to the catalogue
    """
    mag_bins = np.arange(
        float(np.floor(np.min(catalogue.data['magnitude']))) - dmag,
        float(np.ceil(np.max(catalogue.data['magnitude']))) + dmag,
        dmag)
    counter = np.histogram(catalogue.data['magnitude'], mag_bins)[0]
    idx = np.where(counter > 0)[0]
    mag_bins = mag_bins[idx[0]:idx[-1] + 3]
    return mag_bins

def plot_depth_histogram(catalogue, bin_width,  normalisation=False,
        bootstrap=None, filename=None, filetype='png', dpi=300):
    """
    Creates a histogram of the depths in the catalogue
    :param catalogue:
        Earthquake catalogue as instance of :class:
        hmtk.seismicity.catalogue.Catalogue
    :param float bin_width:
        Width of the histogram for the depth bins
    :param bool normalisation:
        Normalise the histogram to give output as PMF (True) or count (False)
    :param int bootstrap:
        To sample depth uncertainty choose number of samples
    """
    plt.figure(figsize=DEFAULT_SIZE)
    # Create depth range
    if len(catalogue.data['depth']) == 0:
        raise ValueError('No depths reported in catalogue!')
    depth_bins = np.arange(0.,
                           np.max(catalogue.data['depth']) + bin_width,
                           bin_width)
    depth_hist = catalogue.get_depth_distribution(depth_bins,
                                                  normalisation,
                                                  bootstrap)
    plt.bar(depth_bins[:-1],
            depth_hist,
            width=0.95 * bin_width,
            edgecolor='k')
    plt.xlabel('Depth (km)', fontsize='large')
    if normalisation:
        plt.ylabel('Probability Mass Function', fontsize='large')
    else:
        plt.ylabel('Count')
    plt.title('Depth Histogram', fontsize='large')

    _save_image(filename, filetype, dpi)
    plt.show()
    return

def plot_magnitude_depth_density(catalogue, mag_int, depth_int, logscale=False,
        normalisation=False, bootstrap=None, filename=None, filetype='png',
        dpi=300):
    """
    Creates a density plot of the magnitude and depth distribution
    :param catalogue:
        Earthquake catalogue as instance of :class:
        hmtk.seismicity.catalogue.Catalogue
    :param float mag_int:
        Width of the histogram for the magnitude bins
    :param float depth_int:
        Width of the histogram for the depth bins
    :param bool logscale:
        Choose to scale the colours in a log-scale (True) or linear (False)
    :param bool normalisation:
        Normalise the histogram to give output as PMF (True) or count (False)
    :param int bootstrap:
        To sample magnitude and depth uncertainties choose number of samples
    """
    if len(catalogue.data['depth']) == 0:
        raise ValueError('No depths reported in catalogue!')
    depth_bins = np.arange(0.,
                           np.max(catalogue.data['depth']) + depth_int,
                           depth_int)
    mag_bins = _get_catalogue_bin_limits(catalogue, mag_int)
    mag_depth_dist = catalogue.get_magnitude_depth_distribution(mag_bins,
                                                                depth_bins,
                                                                normalisation,
                                                                bootstrap)
    vmin_val = np.min(mag_depth_dist[mag_depth_dist > 0.])
    # Create plot
    if logscale:
        normaliser = LogNorm(vmin=vmin_val, vmax=np.max(mag_depth_dist))
    else:
        normaliser = Normalize(vmin=0, vmax=np.max(mag_depth_dist))
    plt.figure(figsize=DEFAULT_SIZE)
    plt.pcolor(mag_bins[:-1],
               depth_bins[:-1],
               mag_depth_dist.T,
               norm=normaliser)
    plt.xlabel('Magnitude', fontsize='large')
    plt.ylabel('Depth (km)', fontsize='large')
    plt.xlim(mag_bins[0], mag_bins[-1])
    plt.ylim(depth_bins[0], depth_bins[-1])
    plt.colorbar()
    if normalisation:
        plt.title('Magnitude-Depth Density', fontsize='large')
    else:
        plt.title('Magnitude-Depth Count', fontsize='large')

    _save_image(filename, filetype, dpi)
    plt.show()
    return

def plot_magnitude_time_scatter(catalogue, plot_error=False, filename=None,
        filetype='png', dpi=300, fmt_string='o'):
    """
    Creates a simple scatter plot of magnitude with time
    :param catalogue:
        Earthquake catalogue as instance of :class:
        hmtk.seismicity.catalogue.Catalogue
    :param bool plot_error:
        Choose to plot error bars (True) or not (False)
    :param str fmt_string:
        Symbology of plot
    """
    plt.figure(figsize=DEFAULT_SIZE)
    dtime = catalogue.get_decimal_time()
    if len(catalogue.data['sigmaMagnitude']) == 0:
        print 'Magnitude Error is missing - neglecting error bars!'
        plot_error = False

    if plot_error:
        plt.errorbar(dtime,
                     catalogue.data['magnitude'],
                     xerr=None,
                     yerr=catalogue.data['sigmaMagnitude'],
                     fmt=fmt_string)
    else:
        plt.plot(dtime, catalogue.data['magnitude'], fmt_string)
    plt.xlabel('Year', fontsize='large')
    plt.ylabel('Magnitude', fontsize='large')
    plt.title('Magnitude-Time Plot', fontsize='large')

    _save_image(filename, filetype, dpi)
    plt.show()
    return

def plot_magnitude_time_density(catalogue, mag_int, time_int,
        normalisation=False, bootstrap=None, filename=None, filetype='png',
        dpi=300):
    """
    Creates a plot of magnitude-time density
    :param catalogue:
        Earthquake catalogue as instance of :class:
        hmtk.seismicity.catalogue.Catalogue
    :param float mag_int:
        Width of the histogram for the magnitude bins
    :param float time_int:
        Width of the histogram for the time bin (in decimal years)
    :param bool normalisation:
        Normalise the histogram to give output as PMF (True) or count (False)
    :param int bootstrap:
        To sample magnitude and depth uncertainties choose number of samples
    """
    plt.figure(figsize=DEFAULT_SIZE)
    # Create the magnitude bins
    if isinstance(mag_int, np.ndarray) or isinstance(mag_int, list):
        mag_bins = mag_int
    else:
        mag_bins = np.arange(
            np.min(catalogue.data['magnitude']),
            np.max(catalogue.data['magnitude']) + mag_int / 2.,
            mag_int)
    # Creates the time bins
    if isinstance(time_int, np.ndarray) or isinstance(time_int, list):
        time_bins = time_int
    else:
        time_bins = np.arange(
            float(np.min(catalogue.data['year'])),
            float(np.max(catalogue.data['year'])) + 1.,
            float(time_int))
    # Get magnitude-time distribution
    mag_time_dist = catalogue.get_magnitude_time_distribution(
        mag_bins,
        time_bins,
        normalisation,
        bootstrap)
    # Get smallest non-zero value
    vmin_val = np.min(mag_time_dist[mag_time_dist > 0.])
    # Create plot
    plt.pcolor(time_bins[:-1],
               mag_bins[:-1],
               mag_time_dist.T,
               norm=LogNorm(vmin=vmin_val, vmax=np.max(mag_time_dist)))
    plt.xlabel('Time (year)', fontsize='large')
    plt.ylabel('Magnitude', fontsize='large')
    plt.xlim(time_bins[0], time_bins[-1])
    plt.colorbar()
    if normalisation:
        plt.title('Magnitude-Time Density', fontsize='large')
    else:
        plt.title('Magnitude-Time Count', fontsize='large')

    _save_image(filename, filetype, dpi)
    plt.show()
    return

def get_completeness_adjusted_table(catalogue, completeness, dmag, end_year):
    """
    Counts the number of earthquakes in each magnitude bin and normalises
    the rate to annual rates, taking into account the completeness
    """
    inc = 1E-7
    # Find the natural bin limits
    mag_bins = _get_catalogue_bin_limits(catalogue, dmag)
    obs_time = end_year - completeness[:, 0] + 1.
    obs_rates = np.zeros_like(mag_bins)
    n_comp = np.shape(completeness)[0]
    for iloc in range(0, n_comp, 1):
        low_mag = completeness[iloc, 1]
        comp_year = completeness[iloc, 0]
        if iloc == n_comp - 1:
            idx = np.logical_and(
                catalogue.data['magnitude'] >= low_mag,
                catalogue.data['year'] >= comp_year - inc)
            high_mag = mag_bins[-1] + dmag
            obs_idx = mag_bins >= (low_mag)
        else:
            high_mag = completeness[iloc + 1, 1]
            mag_idx = np.logical_and(
                catalogue.data['magnitude'] >= low_mag,
                catalogue.data['magnitude'] < high_mag)

            idx = np.logical_and(mag_idx,
                                 catalogue.data['year'] >= comp_year - inc)
            obs_idx = np.logical_and(mag_bins >= low_mag,
                                     mag_bins <= high_mag)
        temp_rates = np.histogram(catalogue.data['magnitude'][idx],
                                  mag_bins[obs_idx])[0]
        print temp_rates.astype(float),obs_time[iloc]
        #print mag_bins[obs_idx], temp_rates
        temp_rates = temp_rates.astype(float) / obs_time[iloc]
        #if iloc == n_comp - 1:
        #    # TODO This hack seems to fix the error in Numpy v.1.8.1
        #    obs_rates[np.where(obs_idx)[0]] = temp_rates
        #else:
        obs_rates[obs_idx[:-1]] = temp_rates
        print "completness :",iloc,completeness[iloc, 1]
        print "search M cat between: ",low_mag,high_mag
        print idx
        print catalogue.data['magnitude'][idx]
        print mag_bins[obs_idx]
        #if len(mag_bins[obs_idx]) == 1:
        #    print "Histo 1 bar",np.histogram(catalogue.data['magnitude'][idx],1)
        #else:
        #    print np.histogram(catalogue.data['magnitude'][idx],mag_bins[obs_idx])
        print len(mag_bins[obs_idx])
        print temp_rates
        
    print "Rates: ",obs_rates
    selector = np.where(obs_rates > 0.)[0]
    mag_bins = mag_bins[selector[0]:selector[-1] + 1]
    obs_rates = obs_rates[selector[0]:selector[-1] + 1]
    # Get cumulative rates
    cum_rates = np.array([sum(obs_rates[iloc:])
                                for iloc in range(0, len(obs_rates))])
    out_idx = cum_rates > 0.
    #print mag_bins[out_idx], obs_rates[out_idx], cum_rates[out_idx]
    return np.column_stack([mag_bins[out_idx],
                            obs_rates[out_idx],
                            cum_rates[out_idx],
                            np.log10(cum_rates[out_idx])])

def plot_observed_recurrence(catalogue, completeness, dmag, end_year=None,
        filename=None, filetype='png', dpi=300):
    """
    Plots the observed recurrence taking into account the completeness
    """
    # Get completeness adjusted recurrence table
    if isinstance(completeness, float):
        # Unique completeness
        completeness = np.array([[np.min(catalogue.data['year']),
                                  completeness]])
    if not end_year:
        end_year = np.max(catalogue.data['year'])
    recurrence = get_completeness_adjusted_table(catalogue,
                                                 completeness,
                                                 dmag,
                                                 end_year)
    plt.figure(figsize=DEFAULT_SIZE)
    plt.semilogy(recurrence[:, 0], recurrence[:, 1], 'bo')
    plt.semilogy(recurrence[:, 0], recurrence[:, 2], 'rs')
    plt.xlim([recurrence[0, 0] - 0.1, recurrence[-1, 0] + 0.1])
    plt.xlabel('Magnitude', fontsize='large')
    plt.ylabel('Annual Rate', fontsize='large')
    plt.legend(['Incremental', 'Cumulative'])

    _save_image(filename, filetype, dpi)
    plt.show()
