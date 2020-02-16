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

import argparse
from tf2_load import tf2_loader
import os

os.environ["LC_MESSAGES"] = "fr"

parser = argparse.ArgumentParser(description='List vehicules')
parser.add_argument('--year', type=int, default=0)
parser.add_argument('--goods', type=str, default=None)
args = parser.parse_args()

GAME_PATH = "../.steam/steam/steamapps/common/Transport Fever 2"

rail_vehicles = tf2_loader(GAME_PATH)

for v in rail_vehicles:
    # filter
    #if not re.search(sys.argv[1], v.name):
    #    continue

    if args.year != 0:
        if v.year_from > args.year:
            continue
        if v.year_to < args.year:
            continue

    if args.goods is not None:
        if args.goods not in v.type:
            continue

    print(str(v))



