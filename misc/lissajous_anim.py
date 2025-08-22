import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import itertools


parser = argparse.ArgumentParser(
    description="Lissajous trajectory animation")

parser.add_argument("-xvel", "--xvel", dest="xvel", default=1, type=float,
    help="angular velocity in x")

parser.add_argument("-yvel", "--yvel", dest="yvel", default=2, type=float,
    help="angular velocity in y")

parser.add_argument("-pts", "--pts", dest="pts", default=1024, type=int,
    help="points to use")


global points_curve, lines

if __name__ == '__main__':
    args = parser.parse_args()
    xvel = float(args.xvel)
    yvel = float(args.yvel)
    
    #points_curve = np.ones((2, args.pts))*np.nan
    points_curve = [[np.nan]*(args.pts-1),[np.nan]*(args.pts-1)]

    x_pos = lambda t: np.sin(xvel*t)
    y_pos = lambda t: np.sin(yvel*t)

    t_vals = np.linspace(-np.pi, np.pi, args.pts)
    t_vals = itertools.cycle(t_vals)

    fig, ax = plt.subplots(1)
    ax.set_xlim(-1.2,1.2)
    ax.set_ylim(-1.2,1.2)
    line, = ax.plot([],[], animated=True)
    line2, = ax.plot(0,0, 'X',color='r', animated=True)
    lines = [line, line2]


    def animation(i):
        global points_curve
        t = next(t_vals)
        x = x_pos(t)
        y = y_pos(t)
        #points_curve[0,-1] = x
        #points_curve[1,-1] = y
        points_curve[0].insert(0,x)
        points_curve[1].insert(0,y)
        points_curve[0].pop()
        points_curve[1].pop()

        lines[0].set_data(points_curve[0], points_curve[1])
        lines[1].set_data([x],[y])
        return lines

    ani = FuncAnimation(fig, animation, blit=True, cache_frame_data=False)
    plt.show()



