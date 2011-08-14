#  Copyright (C) 2011  Groza Cristian
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


#!/bin/sh
F=$1
EXT=${F#*.}

if [ "$EXT" = "py" ] then
    python $1

elif [ "$EXT" = "pl" ] then
    perl $1

elif [ "$EXT" = "perl" ] then
    perl $1

elif [ "$EXT" = "rb" ] then
    irb $1
fi


echo "
------------------
(program exited with code: $?)"
echo "Press return to continue"
#to be more compatible with shells like dash
dummy_var=""
read dummy_var

