# -*- coding: utf-8 -*-
"""
creating a radar chart
"""
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display
from IPython.display import HTML

from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

zhfont = matplotlib.font_manager.FontProperties(fname='./fonts/msyhbd.ttc')

def radar_factory(num_vars, frame='circle'):
    """Create a radar chart.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = 2*np.pi * np.linspace(0, 1-1./num_vars, num_vars)
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        RESOLUTION = 1
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels,fontproperties=zhfont)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)

            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts

def plot_radar(example_data,nVar):
    N = nVar
    theta = radar_factory(N, frame='polygon')

    data = example_data
    people_Num=len(data)
    spoke_labels = data.pop('column names')

    fig = plt.figure(figsize=(9, 2*people_Num))
    fig.subplots_adjust(wspace=0.55, hspace=0.10, top=0.95, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'y']
    for n, title in enumerate(data.keys()):
        ax = fig.add_subplot(int(people_Num/3)+1, 3, n+1, projection='radar')
        plt.rgrids([0.2, 0.4, 0.6, 0.8])
        plt.setp(ax.get_yticklabels(), visible=False)
        plt.ylim([0,1]) 
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),color='b',
                     horizontalalignment='center', verticalalignment='center',fontproperties=zhfont)
        for d, color in zip(data[title], colors):
            ax.plot(theta, d, color=color)
            ax.fill(theta, d, facecolor=color, alpha=0.25)
        ax.set_varlabels(spoke_labels)

    plt.subplot(int(people_Num/3)+1, 3, 1)

    plt.figtext(0.5, 0.965, '战力统计',fontproperties=zhfont,
                ha='center', color='black', weight='bold', size='large')
    plt.show()
