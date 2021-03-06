#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This program help to optimize train composition and choise of vehicle in
#  Transport Fever 2
#
#  Copyright (C) 2020 Benoit Gschwind <gschwind@gnu-log.net>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch
import matplotlib.ticker as ticker
import argparse
from tf2_load import tf2_loader, tf2_load_multiple_unit
import os

from PIL import ImageQt, Image
from matplotlib.colors import Normalize

from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QLineEdit
)

from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtCore import (QSize)


def create_goods_icon(t):
    ret = QLabel()
    pix = global_get_icons(t)
    if pix is not None:
        ret.setPixmap(pix)
    else:
        ret.setText(t)
    return ret

def QtVPack(*args):
    container = QWidget()
    layout = QVBoxLayout(container)
    for a in args:
        layout.addWidget(a)
    return container, layout

def QtHPack(*args):
    container = QWidget()
    layout = QHBoxLayout(container)
    for a in args:
        layout.addWidget(a)
    return container, layout


# @param[in] tpl: list of tuple (title, field)
def create_table(vehicles, selected_vehicle, tpl):

    table = QTableWidget(len(vehicles), len(tpl))
    table.setStyleSheet("QTableView::item { border: 1px black; padding: 2px; } QTableView { margin: 2px; }")
    table.setWordWrap(False)

    for i, (title, field) in enumerate(tpl):
        table.setHorizontalHeaderItem(i, QTableWidgetItem(title))


    table.setColumnWidth(0,20)
    table.setColumnWidth(1,500)
    table.setColumnWidth(2,500)

    for r, v in enumerate(vehicles):
        table.setRowHeight(r, 150)
        # Setup the row
        for c, (title, field) in enumerate(tpl):
            # Check for special field
            if field == "checkbox":
                # Create the heading checkbox
                cb = QCheckBox()
                if v.fileid in selected_vehicle:
                    cb.setCheckState(2)
                def on_change(st, id = v.fileid):
                    nonlocal selected_vehicle
                    if st == 2:
                        selected_vehicle.add(id)
                    else:
                        selected_vehicle.discard(id)
                cb.stateChanged.connect(on_change)
                table.setCellWidget(r, c, cb)
            elif field == "tex":
                tex = global_get_texture(v.tex)
                if tex is not None:
                    ret = QLabel()
                    table.setCellWidget(r, c, ret)
                    pix = QPixmap(tex)
                    pix.scaled(ret.size(), 1)
                    ret.setPixmap(pix)
                    ret.setStyleSheet("margin: 0px; padding: 0px;")
                else:
                    table.setCellWidget(r, c, QLabel("Not Found"))
            elif field == "cargo_type":
                if len(v.cargo_type) == 0:
                    table.setItem(r, c, QTableWidgetItem(""))
                else:
                    ic, _ = QtHPack(*[create_goods_icon(t) for t in v.cargo_type])
                    table.setCellWidget(r, c, ic)
            else:
                table.setItem(r, c, QTableWidgetItem(str(getattr(v, field))))
            pass # all field
        pass # all vehicle

    return table

def create_water_table(vehicles):
    global selected_water_vehicle

    table = create_table(vehicles, selected_water_vehicle, [
        ("",                  "checkbox"),
        ("",                  "tex"),
        ("name",              "name"),
        ("max speed (km/h)",  "xspeed"),
        ("yearly cost",       "running_cost"),
        ("capacity",          "capacity"),
        ("kN",                "max_rpm"),
        ("Mass (t)",          "weight"),
        ("max_rpm",           "max_rpm"),
        ("avail_power",       "avail_power"),
        ("Cargo Type",        "cargo_type"),
        ("File",              "fileid"),
    ])

    table.setColumnWidth(0,20)
    table.setColumnWidth(1,500)
    table.setColumnWidth(2,500)

    return table

def create_road_table(vehicles):
    global selected_road_vehicle

    table = create_table(vehicles, selected_road_vehicle, [
        ("",                  "checkbox"),
        ("",                  "tex"),
        ("name",              "name"),
        ("max speed (km/h)",  "xspeed"),
        ("yearly cost",       "running_cost"),
        ("capacity",          "capacity"),
        ("kN",                "tractive_effort"),
        ("Mass (t)",          "weight"),
        ("Cargo Type",        "cargo_type"),
        ("File",              "fileid"),
    ])

    table.setColumnWidth(0,20)
    table.setColumnWidth(1,500)
    table.setColumnWidth(2,500)

    return table

def create_air_table(vehicles):
    global selected_air_vehicle

    table = create_table(vehicles, selected_air_vehicle, [
        ("",                  "checkbox"),
        ("",                  "tex"),
        ("name",              "name"),
        ("max speed (km/h)",  "xspeed"),
        ("yearly cost",       "running_cost"),
        ("capacity",          "capacity"),
        ("N",                "max_thrust"),
        ("Mass (kg)",          "weight"),
        ("Time to full trust",        "time_to_full_thrust"),
        ("max_take_off_weight",        "max_take_off_weight"),
        ("Cargo Type",        "cargo_type"),
        ("File",              "fileid"),
    ])

    table.setColumnWidth(0,20)
    table.setColumnWidth(1,500)
    table.setColumnWidth(2,500)

    return table

def create_rail_table(vehicles):
    global selected_rail_vehicle

    table = create_table(vehicles, selected_rail_vehicle, [
        ("",                  "checkbox"),
        ("",                  "tex"),
        ("name",              "name"),
        ("max speed (km/h)",  "xspeed"),
        ("yearly cost",       "running_cost"),
        ("capacity",          "capacity"),
        ("kN",                "tractive_effort"),
        ("Mass (t)",          "weight"),
        ("power",             "power"),
        ("Cargo Type",        "cargo_type"),
        ("File",              "fileid"),
    ])

    table.setColumnWidth(0,20)
    table.setColumnWidth(1,500)
    table.setColumnWidth(2,500)

    return table

os.environ["LC_MESSAGES"] = "fr"

parser = argparse.ArgumentParser(description='List vehicules')
parser.add_argument('--year', type=int, default=0)
parser.add_argument('--goods', type=str, default=None)
args = parser.parse_args()

filters_callback = []

# Build the share vehicle filter
def create_general_filter():
    global selected_good

    def apply_filter():
        global filters_callback
        for c in filters_callback:
            c()
        pass

    container = QWidget()
    layout = QHBoxLayout(container)

    qyear = QLineEdit(str(args.year))
    qyear.setMinimumSize(QSize(100,40))
    
    def update_year():
        global selected_year

        try:
            selected_year = int(qyear.text())
            apply_filter()    
        except:
            selected_year = 0
            pass

    qyear.returnPressed.connect(update_year)
    layout.addWidget(qyear)

    for t in all_types:
        pix = global_get_icons(t)
        l = QLabel()
        if pix is not None:
            l.setPixmap(pix)
        else:
            l.setText(t)
        c = QCheckBox()
        if t in selected_good:
            c.setCheckState(2)
        def on_change(st, t=t):
            global selected_good
            if st == 2:
                selected_good.add(t)
            else:
                selected_good.discard(t)
            apply_filter()
        c.stateChanged.connect(on_change)
        ret, _ = QtHPack(c, l)
        layout.addWidget(ret)
        
    for t in ["eu", "usa", "asia"]:
        global selected_region
        c = QCheckBox(t)
        if t in selected_region:
            c.setCheckState(2)
        def on_change(st, t=t):
            global selected_region
            if st == 2:
                selected_region.add(t)
            else:
                selected_region.discard(t)
            apply_filter()
        c.stateChanged.connect(on_change)
        layout.addWidget(c)

    return container

GAME_PATH = os.environ["HOME"]+"/.steam/steam/steamapps/common/Transport Fever 2"
vehicles = tf2_loader(GAME_PATH)

print(tf2_load_multiple_unit(GAME_PATH))

# setup id for each vehicle
for i, v in enumerate(vehicles.rail, 1):
    v.id = i

for i, v in enumerate(vehicles.air, 1):
    v.id = i

all_types = set()
for v in vehicles.rail:
    all_types |= v.cargo_type
for v in vehicles.air:
    all_types |= v.cargo_type
for v in vehicles.water:
    all_types |= v.cargo_type
for v in vehicles.road:
    all_types |= v.cargo_type

def general_vehicle_is_filtered(v):
    global selected_year, selected_good, selected_region

    if v.region not in selected_region:
        return True
    
    if selected_year != 0:
        if v.year_from > selected_year:
            return True
        if v.year_to < selected_year:
            return True
    
    if len(v.cargo_type) == 0:
        return False

    if len(selected_good & v.cargo_type) == 0:
        return True

    return False


app = QApplication([])

# this fonction ensure a texture cache avoid loading same file twice
# static _textures
def global_get_texture(filename, _textures = {}):
    if filename is None:
        return None
    if filename in _textures:
        return _textures[filename]
    with Image.open(filename).convert("RGBA") as im:
        pix = QImage(im.tobytes(), im.size[0], im.size[1], QImage.Format_ARGB32)
        pix = pix.rgbSwapped()
    _textures[filename] = pix
    return pix

# static _goods_pixmap
def global_get_icons(cargo_type, _goods_pixmap = {}):
    if cargo_type in _goods_pixmap:
        return _goods_pixmap[cargo_type]
    tex = os.path.join(GAME_PATH, "res/textures/ui/hud", "cargo_%s@2x.tga"%(cargo_type.lower()))
    if os.path.exists(tex):
        pix = global_get_texture(tex)
        _goods_pixmap[cargo_type] = QPixmap(pix)
    else:
        _goods_pixmap[cargo_type] = None
    return _goods_pixmap[cargo_type]


def filter_table(table, vehicles):
    global selected_year, selected_good, selected_region
    for i, v in enumerate(vehicles):
        if general_vehicle_is_filtered(v):
            table.hideRow(i)
        else:
            table.showRow(i)

selected_region = set(["eu"])
selected_year = 0
if args.goods is not None and args.goods in all_types:
    selected_good = set([args.goods])
else:
    selected_good = set()

window = QMainWindow()
#window.setWidth(1024)
#window.setHeight(800)
central_widget = QTabWidget()
qfilter = create_general_filter()
x, _ = QtVPack(qfilter, central_widget)
window.setCentralWidget(x)


###############################################################################
#
# TRAIN SECTION
#
###############################################################################

train_main_widget = QWidget()
layout = QVBoxLayout(train_main_widget)
central_widget.addTab(train_main_widget, "Train")

qupdate = QPushButton("Show Performance")
layout.addWidget(qupdate)

selected_rail_vehicle = set([v.fileid for v in vehicles.rail])

rail_vehicles_table = create_rail_table(vehicles.rail)
layout.addWidget(rail_vehicles_table)

filters_callback.append(lambda: filter_table(rail_vehicles_table, vehicles.rail))

###############################################################################
#
# AIR SECTION
#
###############################################################################

air_main_widget = QWidget()
layout = QVBoxLayout(air_main_widget)
central_widget.addTab(air_main_widget, "Air")

def do_air_plot():
    # Get selected traction and wagon
    lv = [v for v in vehicles.air if not general_vehicle_is_filtered(v)
          and (v.fileid in selected_air_vehicle)]
    standalone_vehicle_plot(lv)

q_do_air_plot = QPushButton("Show Performance")
layout.addWidget(q_do_air_plot)
q_do_air_plot.clicked.connect(do_air_plot)

selected_air_vehicle = set([v.fileid for v in vehicles.air])

air_vehicles_table = create_air_table(vehicles.air)
layout.addWidget(air_vehicles_table)

filters_callback.append(lambda: filter_table(air_vehicles_table, vehicles.air))

###############################################################################
#
# ROAD SECTION
#
###############################################################################

road_main_widget = QWidget()
layout = QVBoxLayout(road_main_widget)
central_widget.addTab(road_main_widget, "Road")

def do_road_plot():
    # Get selected traction and wagon
    lv = [v for v in vehicles.road if not general_vehicle_is_filtered(v)
          and (v.fileid in selected_road_vehicle)]
    standalone_vehicle_plot(lv)

q_do_road_plot = QPushButton("Show Performance")
layout.addWidget(q_do_road_plot)
q_do_road_plot.clicked.connect(do_road_plot)

selected_road_vehicle = set([v.fileid for v in vehicles.road])

road_vehicles_table = create_road_table(vehicles.road)
layout.addWidget(road_vehicles_table)

filters_callback.append(lambda: filter_table(road_vehicles_table, vehicles.road))

###############################################################################
#
# WATER SECTION
#
###############################################################################

water_main_widget = QWidget()
layout = QVBoxLayout(water_main_widget)
central_widget.addTab(water_main_widget, "Water")

def do_water_plot():
    # Get selected traction and wagon
    lv = [v for v in vehicles.water if not general_vehicle_is_filtered(v)
          and (v.fileid in selected_water_vehicle)]
    standalone_vehicle_plot(lv)

q_do_water_plot = QPushButton("Show Performance")
layout.addWidget(q_do_water_plot)
q_do_water_plot.clicked.connect(do_water_plot)

selected_water_vehicle = set([v.fileid for v in vehicles.water])

water_vehicles_table = create_water_table(vehicles.water)
layout.addWidget(water_vehicles_table)

filters_callback.append(lambda: filter_table(water_vehicles_table, vehicles.water))

###############################################################################
#
# OPTIMIZATION SECTION
#
###############################################################################

def regular_transport_efficentcy(tr, D):
    T = tr.capacity/(2*D/(tr.top_speed*3.6))*12*60
    C = tr.running_cost
    return C/T

def cost(n0, loc, n1, wag):
    return n0*loc.running_cost+n1*wag.running_cost

def acceleration(n0, loc, n1, wag):
    return n0*loc.tractive_effort/(n0*loc.weight+n1*wag.weight)

def rate(n0, loc, n1, wag, D):
    Vc = min(loc.top_speed, wag.top_speed)/3.6
    a = acceleration(n0, loc, n1, wag)
    da = (Vc*Vc)/(2*a)
    t = np.where(D < da, np.sqrt(2*D/a), (2*a*D+Vc*Vc)/(2*a*Vc))
    T = (n0*loc.capacity+n1*wag.capacity)/(2*t)*12*60 # one game year is 12 mins
    return T

# A general fonction for stanalone vehicles
# note: probably wrong for AIR vehicul, they have a huge takeoff and landing overhead
# note: water acceleration is unknown
#
# Hypothesis:
#  - Deceleration is infinite
#  - Make one ride at a time, i.e. goto staion and go back
def standalone_vehicle_plot(vehicles):
    plt.close('all')

    D = np.arange(0,1000)

    plt.figure()
    plt.title("cost per rate, lower is better")
    for v in vehicles:
        V    = v.top_speed
        A    = v.accel
        P    = v.price/6
        C    = v.capacity

        # Distance to reach max speed
        da = (V*V)/A/2
        R = np.where(D<da,
            np.sqrt(2*D)*2*P/(C*np.sqrt(A)),
            (2*A*D+V*V)*P/(A*C*V))
        plt.plot(D, R/(12*60), label=v.name)

    plt.legend()
    plt.show()


def do_plot():
    print('DO PLOT')
    plt.close('all')

    # Get selected traction and wagon
    lv = [v for v in vehicles.rail if not general_vehicle_is_filtered(v)
          and (v.fileid in selected_rail_vehicle)]
    print(lv)

    loc = []
    wag = []
    for v in lv:
        if v.tractive_effort > 0:
            loc.append(v)
        else:
            wag.append(v)

    D, N = np.mgrid[1:100,0:20]
    D *= 100
    names = []
    stats = []
    accel = []
    for l in loc:
        for w in wag:
            names.append(l.name+" + "+w.name)
            C = cost(1, l, N, w)
            T = rate(1, l, N, w, D)
            A = acceleration(1, l, N, w)
            lw_stat = np.full(C.shape, np.inf)
            np.divide(C, T, out=lw_stat, where=T>0.0)
            stats.append(lw_stat)
            accel.append(A)
    stats = np.stack(stats)
    accel = np.stack(accel)
    
    # ensure good acceleration
    stats[accel<0.3] = np.inf

    xmins = np.argsort(stats, axis=0)
    xvals = np.take_along_axis(stats, xmins, axis=0)
    xacce = np.take_along_axis(accel, xmins, axis=0)
    names = np.array(names, dtype='O')

    print("="*80)

    for i in range(1):
        mins = xmins[i,:,:]
        vals = xvals[i,:,:]
        
        # remap and color
        umins = np.unique(mins)
        xnames = names[umins]

        mp = np.zeros((np.max(umins)+1), dtype='i4')
        mp[umins] = np.arange(len(umins), dtype='i4')
        mins = mp[mins]
        print(np.unique(mins))
        
        #ticklabels = ["{:d} km".format(d) for d in range(1,100,10)]
        
        xcm = cm.get_cmap('tab10',10)
        legend_elements = []
        for i, n in enumerate(xnames):
            legend_elements.append(Patch(facecolor=xcm(i),label=n))
        
        fig = plt.figure(dpi=192)
        ax = plt.subplot(121)
        plt.imshow(mins, cmap=xcm, vmax=10, aspect=0.1)
        for a in range(5,mins.shape[0],10):
            for b in range(1, mins.shape[1], 2):
                plt.text(b,a,"%2.0f"%(vals[a, b]/1000), horizontalalignment='center', verticalalignment='center')
        #ax.set_yticklabels(ticklabels)
        ax.set_xlabel("number of wagon")
        ax.xaxis.set_major_locator(ticker.IndexLocator(1,0.5))
        ax.xaxis.set_minor_locator(ticker.IndexLocator(1,0.5))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: "{} km".format(x)))
        ax.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, p: "{} km".format(x)))
        ax = plt.subplot(122)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.axis('off')
        ax.legend(handles=legend_elements, loc='center')#, bbox_to_anchor=(0.5, 1.05))

        plt.figure()
        plt.imshow(xacce[i,:,:], aspect=0.1)

    plt.show()

qupdate.clicked.connect(do_plot)
window.show()
app.exec_()



#
#plt.figure()
#for l in loc:
#    for w in wag:
#        n1, C, T = xplot(loc[l], wag[w], 3000)
#        plt.plot(n1,np.array(C)/np.array(T), label=l+" "+w+" (3000)")
#plt.legend()
#plt.figure()
#for l in loc:
#    for w in wag:
#        n1, C, T = xplot(loc[l], wag[w], 30000)
#        plt.plot(n1,np.array(C)/np.array(T), label=l+" "+w+" (30000)")
#plt.legend()
#plt.show()

## D in meter
#def compute_n(loc, wag, D):
#    Vc = min(loc["Vc"], wag["Vc"])*1000/3600
#    return D*(2*loc["P"]*loc["nd"])/(wag["P"]*wag["M"]*Vc*Vc)\
#           +(loc["P"]*loc["M"])/(wag["P"]*wag["M"])
#
## compute rate (T) for given n0/n1 (n) ratio
#def compute_Tn(loc, wag, n, D):
#    Vc = min(loc["Vc"], wag["Vc"])*1000/3600
#    return (Vc*loc["nd"]*wag["Cu"]*n)/(2*loc["nd"]*D+loc["M"]*Vc*Vc+n*wag["M"]*Vc*Vc)
#
#def compute_n0_n1(loc, wag, T, D):
#    n = compute_n(loc, wag, D)
#    Tn = compute_Tn(loc, wag, n, D)
#    n0 = T/Tn
#    n1 = n0*n
#    return n0, n1
#
#D = np.arange(1,50)*1000
#
#plt.figure()
#plt.plot(D, compute_n(loc, wag, D))
#plt.figure()
#plt.plot(D, compute_Tn(loc, wag, compute_n(loc, wag, D), D))
#plt.show()



