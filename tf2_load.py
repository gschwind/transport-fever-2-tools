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

import gettext
import lupa
from lupa import LuaRuntime
import os, sys
import zipfile
import re
import pickle
import gzip
import math

def lua_has_key(x, k):
    for v in k.split("."):
        if x[v] is None:
            return False
        x = x[v]
    return True
def lua_get_key(x, k):
    for v in k.split("."):
        if x[v] is None:
            return None
        x = x[v]
    return x

def print_compartments(x):
    for a in x.values():
        for b in a.values():
            for c in b.values():
                print("{", c.capacity/4, " ", c.type, "}")

def print_compartments2(x):
    for a in x.values():
        for b in a.loadConfigs.values():
            for c in b.cargoEntries.values():
                print("{", c.capacity/4, " ", c.type, "}")


def read_compartments(x):
    ret = []
    if x['compartments'] is None and x['compartmentsList'] is None:
        return None
    for a in x['compartments'].values() if x['compartmentsList'] is None else x['compartmentsList'].values():
        loadconfigs = []
        for b in (a.values() if a['loadConfigs'] is None else a['loadConfigs'].values()):
            cargo_entries = []
            for c in (b.values() if b['cargoEntries'] is None else b['cargoEntries'].values()):
                cargo_entries.append({ "capacity": c.capacity, "type": c.type })
            loadconfigs.append({'cargo_entries': cargo_entries})
        ret.append({'loadconfigs': loadconfigs})
    return ret

def read_engines(x):
    engines = []
    for a in x.values():
        engines.append({"tractive_effort": a.tractiveEffort, "power": a.power, "type": a.type})
    return engines
    

def print_engines_rail(x):
    if not lua_has_key(x, "metadata.railVehicle.engines"):
        return
    x = lua_get_key(x, "metadata.railVehicle.engines")
    for a in x.values():
        print("metadata.railVehicle.engines = {", a.tractiveEffort, "nd, ", a.power, "kW, ", a.type, "}")

def print_engines_road(x):
    if not lua_has_key(x, "metadata.roadVehicle.engines"):
        return
    x = lua_get_key(x, "metadata.roadVehicle.engines")
    for a in x.values():
        print("metadata.roadVehicle.engines = {", a.tractiveEffort, "nd, ", a.power, "kW, ", a.type, "}")


def print_x(x, n):
    for v in n.split("."):
        if x[v] is None:
            return
        x = x[v]
    print(n, " = ", x)

def print_lua(x, s = ""):
    if lupa.lua_type(x) == 'table':
        for k, v in x.items():
            if k in ['seatProvider','configs','soundSet']:
                continue
            print(s, k)
            print_lua(v, s+"  ")
    else:
        print(s, x)


class rail_vehicle():
    def __init__(self, metadata):
        if not lua_has_key(metadata, "description.name"):
            self.name = "no name"
        else:
            self.name = metadata.description.name
        self.year_from = metadata.availability.yearFrom
        self.year_to = metadata.availability.yearTo
        if self.year_to == 0:
            self.year_to = 2147483647
        self.lifespan = metadata.maintenance.lifespan
        self.compartments = read_compartments(metadata.transportVehicle)
        self.top_speed = metadata.railVehicle.topSpeed
        self.weight = metadata.railVehicle.weight
        self.engines = read_engines(metadata.railVehicle.engines)
        self.tractive_effort = 0
        self.power = 0
        for e in self.engines:
            self.tractive_effort += e['tractive_effort']
            self.power += e['power']
        self.capacity = 0
        self.type = set()
        if self.compartments is not None:
            for cp in self.compartments:
                for ca in cp['loadconfigs'][0]['cargo_entries']:
                    self.capacity += ca['capacity']
                for ca in cp['loadconfigs']:
                    for e in ca['cargo_entries']:
                        self.type |= set([e['type']])
        # Guessed from data gathered, speed is converted to km/h
        self.price = 3600*self.power+150*self.capacity*self.top_speed*3600/1000
        # Guessed from data
        self.running_cost = self.price/6

    def __str__(self):
        return "{0.name} ({0.running_cost:.0f}) {1} km/h {0.weight} t {0.tractive_effort} kN {0.capacity} {0.type}".format(self, math.floor(self.top_speed*3600/1000+0.5))

def tf2_loader(GAME_PATH, use_cache = False):
    # quick reload of data
    xdata = None
    p = ".cache/vehicle.dat"
    if False:
        try:
            with gzip.open(p, "rb") as f:
                xdata = pickle.load(f)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pass

    if xdata is None:
        xdata = {}

        # load base data
        odata = {}
        MDL_FILES_PATTERN = re.compile("^model/vehicle/.*\.mdl$")
        with zipfile.ZipFile(os.path.join(GAME_PATH,"res","models","models.zip"),"r") as f:
            for i in f.infolist():
                if MDL_FILES_PATTERN.match(i.filename):
                    print("Load file", i.filename)
                    odata[i.filename] = f.read(i).decode("utf-8")
        xdata["."] = odata


        # Loading mods files
        MDL_FILES_PATTERN2 = re.compile("^res/models/model/vehicle/.*\.mdl$")
        mods_root_path = os.path.join(GAME_PATH,"mods")
        for d in os.listdir(mods_root_path):
            odata = {}
            mod_path = os.path.join(mods_root_path, d)
            for root, directories, files in os.walk(mod_path):
                for f in files:
                    abs_filename = os.path.join(root, f)
                    rel_filename = abs_filename[len(mod_path)+1:]
                    if not MDL_FILES_PATTERN2.match(rel_filename):
                        continue
                    print("Load file", os.path.join(d, rel_filename[11:]))
                    with open(abs_filename,"rb") as f:
                        odata[rel_filename[11:]] = f.read().decode("utf-8")
            xdata[os.path.join(".","mods",d)] = odata
        if use_cache:
            os.makedirs(".cache", 0o700, True)
            with gzip.open(p, "wb") as f:
                pickle.dump(xdata, f)
        
    lua = LuaRuntime(unpack_returned_tuples=True)

    # setup lua to take care of gettext
    gettext.bindtextdomain("res", localedir=os.path.join(GAME_PATH,"res","strings"))
    gettext.bindtextdomain("base", localedir=os.path.join(GAME_PATH,"res","strings"))
    gettext.textdomain("res")

    lua.globals()["_"] = gettext.gettext

    # Enable lookup for game includes
    lua.globals().package.path = lua.globals().package.path + ";" + os.path.join(GAME_PATH, "res", "scripts", "?.lua")

    TEXTURE_PATH = os.path.join(GAME_PATH, "res/textures/ui/models_small")
        
    rail_vehicles = []
        
    for k0, v0 in xdata.items():
        print(k0)
        tmp_data = {}
        for k, v in v0.items():
            try:
                lua.execute(v)
                tmp_data[k] = lua.globals()["data"]()
            except Exception as e:
                print(v)
                print(e)

        for k, x in tmp_data.items():
            if not lua_has_key(x, "metadata.transportVehicle.carrier"):
                continue
            if not lua_has_key(x, "metadata.description.name"):
                name = k
            else:
                name = x.metadata.description.name

            carrier = str(x.metadata.transportVehicle.carrier)

            if carrier == "RAIL":
                rail_vehicles.append(rail_vehicle(x.metadata))
                rail_vehicles[-1].file = k
                rail_vehicles[-1].mods = k0
                if re.search("\/asia\/", k):
                    rail_vehicles[-1].region = "asia"
                elif re.search("\/usa\/", k):
                    rail_vehicles[-1].region = "usa"
                else:
                    rail_vehicles[-1].region = "eu"
            if carrier == "ROAD":
                pass
            if carrier == "TRAM":
                pass
            if carrier == "WATER":
                pass
            if carrier == "AIR":
                pass

    return rail_vehicles

#    for k, x in xdata.items():
#        print("="*80)
#        print(k)
#        if not lua_has_key(x, "metadata.transportVehicle.carrier"):
#            continue
#        if not lua_has_key(x, "metadata.description.name"):
#            name = k
#        else:
#            name = x.metadata.description.name
#        
#
#        carrier = str(x.metadata.transportVehicle.carrier)
#
#        #print_lua(x.metadata)
#        print_x(x, "metadata.availability.yearFrom")
#        print_x(x, "metadata.availability.yearTo")
#        print_x(x, "metadata.maintenance.lifespan")
#        if carrier == "RAIL":
#            print_x(x, "metadata.railVehicle.weight")
#            print_x(x, "metadata.railVehicle.topSpeed")
#            print_engines_rail(x)
#        if carrier == "ROAD":
#            print_x(x, "metadata.roadVehicle.weight")
#            print_x(x, "metadata.roadVehicle.topSpeed")
#            print_engines_road(x)
#        if carrier == "TRAM":
#            print_x(x, "metadata.railVehicle.weight")
#            print_x(x, "metadata.railVehicle.topSpeed")
#            print_engines_rail(x)
#        if carrier == "WATER":
#            print_x(x, "metadata.waterVehicle.topSpeed")
#            print_x(x, "metadata.waterVehicle.availPower")
#        if carrier == "AIR":
#            print_x(x, "metadata.airVehicle.topSpeed")
#            print_x(x, "metadata.airVehicle.weight")
#        if lua_has_key(x, "metadata.transportVehicle.compartments"):
#            print_compartments(lua_get_key(x, "metadata.transportVehicle.compartments"))
#        if lua_has_key(x, "metadata.transportVehicle.compartmentsList"):
#            print_compartments2(lua_get_key(x, "metadata.transportVehicle.compartmentsList"))
#        print_x(x, "version")
    


