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
from tf2_load import tf2_loader
import os

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
    QLineEdit
)

def create_table(loc, parent = None):
    table = QTableWidget(len(loc), 9, parent)
    table.setWordWrap(False)
    table.setHorizontalHeaderItem(0, QTableWidgetItem(""))
    table.setHorizontalHeaderItem(1, QTableWidgetItem(""))
    table.setHorizontalHeaderItem(2, QTableWidgetItem("name"))
    table.setHorizontalHeaderItem(3, QTableWidgetItem("max speed (km/h)"))
    table.setHorizontalHeaderItem(4, QTableWidgetItem("yearly cost"))
    table.setHorizontalHeaderItem(5, QTableWidgetItem("capacity"))
    table.setHorizontalHeaderItem(6, QTableWidgetItem("kN"))
    table.setHorizontalHeaderItem(7, QTableWidgetItem("Mass (t)"))
    table.setHorizontalHeaderItem(8, QTableWidgetItem("Types"))

    table.setColumnWidth(0,10)
    table.setColumnWidth(1,10)
    table.setColumnWidth(2,500)

    lcb = []
    for i, l in enumerate(loc):
        lcb.append(QCheckBox(""))
        lcb[-1].setCheckState(2)
        table.setCellWidget(i, 0, lcb[-1])
        table.setItem(i, 1, QTableWidgetItem("W" if l.tractive_effort <= 0 else "T"))
        table.setItem(i, 2, QTableWidgetItem(str(l.name)))
        table.setItem(i, 3, QTableWidgetItem("%.0f"%np.round(l.top_speed*3.6)))
        table.setItem(i, 4, QTableWidgetItem("%.0f"%l.running_cost))
        table.setItem(i, 5, QTableWidgetItem(str(l.capacity/4)))
        table.setItem(i, 6, QTableWidgetItem(str(l.tractive_effort)))
        table.setItem(i, 7, QTableWidgetItem(str(l.weight)))
        table.setItem(i, 8, QTableWidgetItem(str(l.type)))
    return table, lcb

os.environ["LC_MESSAGES"] = "fr"

parser = argparse.ArgumentParser(description='List vehicules')
parser.add_argument('--year', type=int, default=0)
parser.add_argument('--goods', type=str, default=None)
args = parser.parse_args()

GAME_PATH = "../.steam/steam/steamapps/common/Transport Fever 2"

rail_vehicles = tf2_loader(GAME_PATH)

def filter_data(year, goods):
    loc = []
    wag = []
    for v in rail_vehicles:
        # filter
        #if not re.search(sys.argv[1], v.name):
        #    continue

        if args.year != 0:
            if v.year_from > year:
                continue
            if v.year_to < year:
                continue
        
        if v.tractive_effort > 0:
            loc.append(v)

        if goods is not None:
            if goods not in v.type:
                continue
        
        if v.tractive_effort <= 0:
            wag.append(v)
    return loc, wag


plt.close('all')


app = QApplication([])

window = QMainWindow()
#window.setWidth(1024)
#window.setHeight(800)
xx = QWidget()
window.setCentralWidget(xx)
layout = QVBoxLayout(xx)

topbar = QWidget()
layout.addWidget(topbar)

layouttopbar = QHBoxLayout(topbar)

def update_filter():
    global tablea, tableb, qyear, qgood
    try:
        year = int(qyear.text())
    except:
        year = 0

    goods = qgood.text()
    if len(goods) == 0:
        goods = None
    if goods == 'None':
        goods = None
    loc, wag = filter_data(year, goods)
    tableaa, lcb = create_table(loc+wag, xx)
    layout.replaceWidget(tablea, tableaa)
    tablea = tableaa
    #tablebb, wcb = create_table(wag, xx)
    #layout.replaceWidget(tableb, tablebb)
    #tableb = tablebb

qyear = QLineEdit(str(args.year), topbar)
qyear.returnPressed.connect(update_filter)
layouttopbar.addWidget(qyear)

qgood = QLineEdit(str(args.goods), topbar)
qgood.returnPressed.connect(update_filter)
layouttopbar.addWidget(qgood)

qupdate = QPushButton("OK")
layouttopbar.addWidget(qupdate)
qupdate.clicked.connect(lambda: app.quit())

loc, wag = filter_data(args.year, args.goods)
tablea, lcb = create_table(loc+wag, xx)
layout.addWidget(tablea)
#tableb, wcb = create_table(wag, xx)
#layout.addWidget(tableb)

window.show()
app.exec_()

#loc = {
#    "PLM 220": {
#        "Cu": 0,
#        "Vc": 60, # km/h to conver to m/s
#        "nd": 75, # t.m.s^{-2}
#        "M": 57, # Mass in tone
#        "P": 271971 # Cost in $/year
#    },
#    "BR 53 preuss. G3": {
#        "Cu": 0,
#        "Vc": 50, # km/h to conver to m/s
#        "nd": 50, # t.m.s^{-2}
#        "M": 38, # Mass in tone
#        "P": 121377 # Cost in $/year
#    },
#    "BR 89 preuss. T3": {
#        "Cu": 0,
#        "Vc": 40, # km/h to conver to m/s
#        "nd": 40, # t.m.s^{-2}
#        "M": 30, # Mass in tone
#        "P": 131181 # Cost in $/year
#    },
#    "A 3/5": {
#        "Cu": 0,
#        "Vc": 100, # km/h to conver to m/s
#        "nd": 115, # t.m.s^{-2}
#        "M": 107, # Mass in tone
#        "P": 617347 # Cost in $/year
#    },
#    "2-8-2 Mikado": {
#        "Cu": 0,
#        "Vc": 80, # km/h to conver to m/s
#        "nd": 228, # t.m.s^{-2}
#        "M": 219, # Mass in tone
#        "P": 713535 # Cost in $/year
#    },
#    "MILW-Class EP-2": {
#        "Cu": 0,
#        "Vc": 120, # km/h to conver to m/s
#        "nd": 516, # t.m.s^{-2}
#        "M": 240, # Mass in tone
#        "P": 2080376 # Cost in $/year
#    },
#    "BR 75.4 bad. VI c": {
#        "Cu": 0,
#        "Vc": 90, # km/h to conver to m/s
#        "nd": 85, # t.m.s^{-2}
#        "M": 76, # Mass in tone
#        "P": 355224 # Cost in $/year
#    },
#    "Ce 6/8 II Crocodile": {
#        "Cu": 0,
#        "Vc": 75, # km/h to conver to m/s
#        "nd": 150, # t.m.s^{-2}
#        "M": 128, # Mass in tone
#        "P": 1000943 # Cost in $/year
#    },
#    "Ae 4/7": {
#        "Cu": 0,
#        "Vc": 100, # km/h to conver to m/s
#        "nd": 196, # t.m.s^{-2}
#        "M": 121, # Mass in tone
#        "P": 1419898 # Cost in $/year
#    },
#    "CLe 2/4 Roter Pfeil": {
#        "Cu": 20,
#        "Vc": 125, # km/h to conver to m/s
#        "nd": 45, # t.m.s^{-2}
#        "M": 33, # Mass in tone
#        "P": 451309 # Cost in $/year
#    }
#}
#
#wag = {
#    "Wagon convert #0": {
#        "Cu": 8, # capacity un tone
#        "Vc": 80, # max speed in km/h
#        "M": 11, # in tone
#        "P": 62290, #  Cost in $/year
#    },
#    "Wagon convert #1": {
#        "Cu": 4, # capacity un tone
#        "Vc": 50, # max speed in km/h
#        "M": 5, # in tone
#        "P": 19420, #  Cost in $/year
#    },
#    "Wagon a compartiment separer": {
#        "Cu": 11, # capacity un tone
#        "Vc": 60, # max speed in km/h
#        "M": 10, # in tone
#        "P": 63822, #  Cost in $/year
#    },
#    "Wagon a six roues": {
#        "Cu": 14, # capacity un tone
#        "Vc": 100, # max speed in km/h
#        "M": 15, # in tone
#        "P": 138286, #  Cost in $/year
#    },
#    "Voiture de passager pour le sultant": {
#        "Cu": 20, # capacity un tone
#        "Vc": 100, # max speed in km/h
#        "M": 40, # in tone
#        "P": 197551, #  Cost in $/year
#    },
#    "Wagon plat a rancher #0": {
#        "Cu": 4, # capacity un tone
#        "Vc": 50, # max speed in km/h
#        "M": 5, # in tone
#        "P": 19420, #  Cost in $/year
#    },
#    "Wagon plat a rancher #1": {
#        "Cu": 8, # capacity un tone
#        "Vc": 80, # max speed in km/h
#        "M": 10, # in tone
#        "P": 62290, #  Cost in $/year
#    },
#    "Wagon-citern": {
#        "Cu": 5, # capacity un tone
#        "Vc": 50, # max speed in km/h
#        "M": 6, # in tone
#        "P": 24275, #  Cost in $/year
#    },
#    "Wagon-citerne #2": {
#        "Cu": 12, # capacity un tone
#        "Vc": 80, # max speed in km/h
#        "M": 15, # in tone
#        "P": 93435, #  Cost in $/year
#    },
#    "Boite a tonnerre": {
#        "Cu": 17, # capacity un tone
#        "Vc": 100, # max speed in km/h
#        "M": 20, # in tone
#        "P": 167918, #  Cost in $/year
#    },
#    "Wagon-tombereau": {
#        "Cu": 8, # capacity un tone
#        "Vc": 80, # max speed in km/h
#        "M": 10, # in tone
#        "P": 62290, #  Cost in $/year
#    },
#    "BC4": {
#        "Cu": 20, # capacity un tone
#        "Vc": 120, # max speed in km/h
#        "M": 24, # in tone
#        "P": 241276, #  Cost in $/year
#    },
#}
#    
def regular_transport_efficentcy(tr, D):
    T = tr.capacity/(2*D/(tr.top_speed*3.6))*12*60
    C = tr.running_cost
    return C/T
    
    
SELECT_LOC = ["CLe 2/4 Roter Pfeil","Ae 4/7","A 3/5","BR 75.4 bad. VI c","Ce 6/8 II Crocodile"]
SELECT_WAG = ["BC4","Wagon a six roues","Boite a tonnerre",]

def cost(n0, loc, n1, wag):
    return n0*loc.running_cost+n1*wag.running_cost

def rate(n0, loc, n1, wag, D):
    Vc = min(loc.top_speed, wag.top_speed)/3.6
    a = n0*loc.tractive_effort/(n0*loc.weight+n1*wag.weight)
    da = (Vc*Vc)/(2*a)
    if D < da: # if the train never reach Vc
        t = np.sqrt(2*D/a)
    else:
        t = D/Vc + Vc/a
    T = (n0*loc.capacity+n1*wag.capacity)/(2*t)*12*60 # one game year is 12 mins
    return T

def xplot(loc, wag, D):
    N = 20
    n1 = range(0,N)
    C = [cost(1, loc, n, wag) for n in n1]
    T = [rate(1, loc, n, wag, D) for n in n1]
    return n1, C, T

names = []
stats = []
for l in loc:
    for w in wag:
        names.append(l.name+" + "+w.name+" (3000)")
        n1, C, T = xplot(l, w, 3000)
        C = np.array(C)
        T = np.array(T)
        perf = np.empty(C.shape)
        perf[:] = np.inf
        np.divide(C, T, out=perf, where=T>0.0)
        stats.append(perf)

stats = np.array(stats)
print(stats.shape)
m = np.argmin(stats, axis=0)

for i in range(len(m)):
    print("{}: {} <{}>".format(n1[i], names[m[i]], stats[m[i],i]))

plt.figure()
plt.plot([stats[m[i],i] for i in range(len(m))])

mins = []
xstats = []

for d in range(1,100):
    names = []
    stats = []
    for l in loc:
        for w in wag:
            names.append(l.name+" + "+w.name)
            n1, C, T = xplot(l, w, d*1000)
            stats.append(np.array(C)/np.array(T))    
    stats = np.array(stats)
    xstats.append(stats)
    m = np.argsort(stats, axis=0)
    mins.append(m)

xstats = np.array(xstats)
xmins = np.array(mins)
print(xmins.shape)

for i in range(2):
    mins = xmins[:,i,:]
    umins = np.unique(mins)
    
    print(names)
    mp = np.zeros((np.max(umins)+1), dtype='i4')
    mp[umins] = np.arange(len(umins), dtype='i4')
    mins = mp[mins]
    print(np.unique(mins))
    xnames = np.array(names, dtype='O')[umins]
    
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
            plt.text(b,a,"%2.0f"%(xstats[a, mins[a,b], b]/1000), horizontalalignment='center', verticalalignment='center')
    #ax.set_yticklabels(ticklabels)
    ax.set_xlabel("number of wagon")
    ax.xaxis.set_major_locator(ticker.IndexLocator(1,0.5))
    ax.xaxis.set_minor_locator(ticker.IndexLocator(1,0.5))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: "{} km".format(x)))
    ax.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, p: "{} km".format(x)))
    ax = plt.subplot(122)
    ax.legend(handles=legend_elements, loc='center')#, bbox_to_anchor=(0.5, 1.05))


plt.show()



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



