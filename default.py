"""patience game selector

Copyright Chetan Padia (chetbox@users.noreply.github.com)
Released under GPLv3 (See COPYING.txt)
"""

# This file is part of Patience for S60.
#
# Patience for S60 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Patience for S60 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# SYMBIAN_UID = 0x2000D023

from appuifw import popup_menu
from sys import exit

# show the menu
title = u'Choose a game:'
menu = [
 u'Solitaire (draw 3)',
 u'Solitaire (draw 1)',
 u'FreeCell',
]

choice = popup_menu(menu, title)

if choice == 0:
 import solitaire
 solitaire.Game(difficulty = 3)

if choice == 1:
 import solitaire
 solitaire.Game(difficulty = 1)

if choice == 2:
 import freecell
 freecell.Game()

exit()
