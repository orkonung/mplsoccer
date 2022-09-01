"""`mplsoccer.quiver` is a python module containing a function to plot arrows in
Matplotlib and a complementary handler for adding the arrows to the legend."""

import numpy as np
from matplotlib import patches
from matplotlib.legend import Legend
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.quiver import Quiver

from mplsoccer.utils import validate_ax

__all__ = ['arrows']


def arrows(xstart, ystart, xend, yend, *args, ax=None, vertical=False, **kwargs):
    """ Utility wrapper around matplotlib.axes.Axes.quiver.
    Quiver uses locations and direction vectors usually.
    Here these are instead calculated automatically
    from the start and endpoints of the arrow.
    The function also automatically flips the x and y coordinates if the pitch is vertical.

    Plot a 2D field of arrows.
    See: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.quiver.html

    Parameters
    ----------
    xstart, ystart, xend, yend: array-like or scalar.
        Commonly, these parameters are 1D arrays.
        These should be the start and end coordinates of the lines.
    C: 1D or 2D array-like, optional
        Numeric data that defines the arrow colors by colormapping via norm and cmap.
        This does not support explicit colors.
        If you want to set colors directly, use color instead.
        The size of C must match the number of arrow locations.
    ax : matplotlib.axes.Axes, default None
        The axis to plot on.
    vertical : bool, default False
        If the orientation is vertical (True), then the code switches the x and y coordinates.
    width : float, default 4
        Arrow shaft width in points.
    headwidth : float, default 3
        Head width as a multiple of the arrow shaft width.
    headlength : float, default 5
        Head length as a multiple of the arrow shaft width.
    headaxislength : float, default: 4.5
        Head length at the shaft intersection.
        If this is equal to the headlength then the arrow will be a triangular shape.
        If greater than the headlength then the arrow will be wedge shaped.
        If less than the headlength the arrow will be swept back.
    color : color or color sequence, optional
        Explicit color(s) for the arrows. If C has been set, color has no effect.
    linewidth or linewidths or lw : float or sequence of floats
        Edgewidth of arrow.
    edgecolor or ec or edgecolors : color or sequence of colors or 'face'
    alpha : float or None
        Transparency of arrows.
    **kwargs : All other keyword arguments are passed on to matplotlib.axes.Axes.quiver.

    Returns
    -------
    PolyCollection : matplotlib.quiver.Quiver

    Examples
    --------
    >>> from mplsoccer import Pitch
    >>> pitch = Pitch()
    >>> fig, ax = pitch.draw()
    >>> pitch.arrows(20, 20, 45, 80, ax=ax)

    >>> from mplsoccer.quiver import arrows
    >>> import matplotlib.pyplot as plt
    >>> fig, ax = plt.subplots()
    >>> arrows([0.1, 0.4], [0.1, 0.5], [0.9, 0.4], [0.8, 0.8], ax=ax)
    >>> ax.set_xlim(0, 1)
    >>> ax.set_ylim(0, 1)
    """
    validate_ax(ax)

    # set so plots in data units
    units = kwargs.pop('units', 'inches')
    scale_units = kwargs.pop('scale_units', 'xy')
    angles = kwargs.pop('angles', 'xy')
    scale = kwargs.pop('scale', 1)
    width = kwargs.pop('width', 4)
    # fixed a bug here. I changed the units to inches and divided by 72
    # so the width is in points, i.e. 1/72th of an inch
    width = width / 72.

    xstart = np.ravel(xstart)
    ystart = np.ravel(ystart)
    xend = np.ravel(xend)
    yend = np.ravel(yend)

    if xstart.size != ystart.size:
        raise ValueError("xstart and ystart must be the same size")
    if xstart.size != xend.size:
        raise ValueError("xstart and xend must be the same size")
    if ystart.size != yend.size:
        raise ValueError("ystart and yend must be the same size")

    # vectors for direction
    u = xend - xstart
    v = yend - ystart

    if vertical:
        ystart, xstart = xstart, ystart
        v, u = u, v

    q = ax.quiver(xstart, ystart, u, v, *args,
                  units=units, scale_units=scale_units, angles=angles,
                  scale=scale, width=width, **kwargs)

    quiver_handler = HandlerQuiver()
    Legend.update_default_handler_map({Quiver: quiver_handler})

    return q


class HandlerQuiver(HandlerLine2D):
    """Automatically generated by mplsoccer's arrows() to allow use of arrows in legend.
    """
    def create_artists(self, legend, orig_handle, xdescent, ydescent,
                       width, height, fontsize, trans):
        xdata, _ = self.get_xdata(legend, xdescent, ydescent, width, height, fontsize)
        ydata = ((height - ydescent) / 2.) * np.ones(len(xdata), float)
        # I divide by 72 in the quiver plot so have to multiply
        # back here as the legend is in different units
        width = orig_handle.width * 72.
        head_width = width * orig_handle.headwidth
        head_length = width * orig_handle.headlength
        overhang = (orig_handle.headlength - orig_handle.headaxislength)/orig_handle.headlength
        edgecolor = orig_handle.get_edgecolor()
        facecolor = orig_handle.get_facecolor()
        edgecolor = None if len(edgecolor) == 0 else edgecolor[0]
        facecolor = None if len(facecolor) == 0 else facecolor[0]
        legline = patches.FancyArrow(x=xdata[0],
                                     y=ydata[0],
                                     dx=xdata[-1]-xdata[0],
                                     dy=ydata[-1]-ydata[0],
                                     head_width=head_width,
                                     head_length=head_length,
                                     overhang=overhang,
                                     length_includes_head=True,
                                     width=width,
                                     lw=orig_handle.get_linewidths()[0],
                                     edgecolor=edgecolor,
                                     facecolor=facecolor)
        legline.set_transform(trans)
        return [legline]
