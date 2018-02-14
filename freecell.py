"""freecell game

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


# depends on the 'cards' library to draw cards
from cards import *
import cards
from e32 import Ao_lock
from appuifw import app, note, query
from key_codes import EKeyUpArrow, EKeyDownArrow, EKeyLeftArrow, EKeyRightArrow, EKeyBackspace, EKeySelect

cardWidth = cards.cardWidth = 20
cardHeight = cards.cardHeight = 35

class Game:

 def __init__(self):
  self.columns = range(1,9)
  self.free = range(1,5)
  self.suits = range(1,5)
  self.table = Table (initialCards = Deck(visible = True))
  self.selected = None
  self.deal(self.table)
  self.select(('game',1))
  self.table.show()
  self.registerKeys()
  self.lock = Ao_lock()
  self.lock.wait()
  self.table.unshow()

 def deal(self, table):
  pile = table[('pile',1)]
  pile.cascadeY = 0
  pile.shuffle()
  pile.drawBase = False
  # add free card stacks
  for free in self.free:
   table.addStack(id = ('free',free))
   table[('free',free)].x = 1 + cardWidth * free - cardWidth / 2
  # add goal stacks
  x = 4 * (cardWidth + 1) + cardWidth / 2 + 2
  goal = 0
  for suit in self.suits:
   table.addStack(id = ('goal', suit))
   table[('goal', suit)].x = x
   table[('goal', suit)].y = 1
   table[('goal', suit)].cascadeX = 0
   table[('goal', suit)].cascadeY = 0
   x += cardWidth
  x = cardWidth / 2 + 1
  for col in self.columns:
   table.addStack(id = ('game', col))
   table[('game', col)].x = x
   table[('game', col)].y = 45
   table[('game', col)].cascadeX = 0
   table[('game', col)].cascadeY = 10
   x += cardWidth + 1
  while len(pile) > 0:
   for col in self.columns:
    table.moveCards(pile, self.table[('game', col)], 1)
  # add temporary cards for held stack
  table.addStack(id = ('held',1))
  table[('held',1)].x = 60
  table[('held',1)].y = 180
  table[('held',1)].cascadeX = 12
  table[('held',1)].cascadeY = 4
  table[('held',1)].drawBase = False
  self.held = table[('held',1)]

 def select(self, stackName, index = -1):
  sel = self.selected
  if sel:
   self.table[sel].selectedIndex = None
  self.table[stackName].selectedIndex = index
  self.selected = stackName

 def registerKeys(self):
  table = app.body
  table.bind(EKeyDownArrow, self.keyDown)
  table.bind(EKeyUpArrow, self.keyUp)
  table.bind(EKeyRightArrow, self.keyRight)
  table.bind(EKeyLeftArrow, self.keyLeft)
  table.bind(EKeySelect, self.keySelect)
  app.exit_key_handler = self.exit

 def exit(self):
  if query(u'Exit game','query'):
   self.lock.signal()

 def keyUp(self):
  sel = self.selected
  stack = self.table[sel]
  # find no. of free cells
  n = 0
  for free in self.free:
   if len(self.table[('free',free)]) == 0:
    n += 1
  if len(stack[:stack.selectedIndex]) > 0 and stack[stack.selectedIndex - 1].visible and n >= len(stack[stack.selectedIndex:]) and sel[0] == 'game' and stack[stack.selectedIndex].colour() != stack[stack.selectedIndex - 1].colour() and int(stack[stack.selectedIndex]) + 1 == int(stack[stack.selectedIndex - 1]):
   self.select(sel, stack.selectedIndex - 1)
  self.table.refreshMarkers()

 def keyDown(self):
  sel = self.selected
  stack = self.table[sel]
  if len(stack[stack.selectedIndex:]) > 1:
   self.select(sel, stack.selectedIndex + 1)
  else:
   if sel[0] == 'free':
    self.select(('game',sel[1]), -1)
   if sel[0] == 'goal':
    self.select(('game',sel[1] + len(self.free)), -1)
  self.table.refreshMarkers()

 def keySelect(self):
  sel = self.selected
  stack = self.table[sel]
  card = stack.selected()
  pile = self.table[('pile',1)]
  free = self.table[('free',1)]
  if sel[0] == 'game' or sel[0] == 'goal' or sel[0] == 'free':
   if len(self.held) > 0:
    # drop cards if possible
    if (sel[0] == 'free' and len(stack) == 0 and len(self.held) == 1) or (sel[0] == 'game' and len(stack) == 0) or (len(stack) == 0 and sel[0] == 'goal' and int(self.held[0]) == 1 and len(self.held) == 1) or (sel[0] == 'goal' and len(stack) > 0 and stack[-1].suit() == self.held[0].suit() and int(stack[-1]) - int(self.held[0]) == -1 and len(self.held) == 1) or (stack == self.prevStack) or (sel[0] == 'game' and len(stack) > 0 and int(stack[-1]) - int(self.held[0]) == 1 and stack[-1].colour() != self.held[0].colour()):
     self.table.moveCards(self.held, stack)
     self.select(sel)
     self.table.refresh()
     # check if the game is finished
     finished = True
     for suit in self.suits:
      finished &= len(self.table[('goal',suit)]) == 13
     if finished:
      note(u'Complete!','conf')
      self.lock.signal()
     return
   # pick up selected cards
   else:
    if card and card.visible:
     self.table.moveCards(stack, self.held, len(stack[stack.selectedIndex:]))
     self.prevStack = stack
     self.select(sel)
     self.table.refresh()
     return
  # return the cards if position invalid
  if len(self.held) > 0:
   self.table.moveCards(self.held, self.prevStack)
   self.table.refresh()

 def keyLeft(self):
  sel = self.selected
  if sel[0] == 'game':
   new = sel[1] - 1
   if new in self.columns:
    self.select((sel[0], new))
   else:
    self.select(('goal',max(self.suits)))
  if sel[0] == 'goal':
   new = sel[1] - 1
   if new in self.suits:
    self.select((sel[0], new))
   else:
    self.select(('free',max(self.free)))
  if sel[0] == 'free':
   new = sel[1] - 1
   if new in self.free:
    self.select((sel[0], new))
   else:
    self.select(('game', max(self.columns)))
  sel = self.selected
  stack = self.table[sel]
  if len(self.held) == 0 and len(stack) == 0:
   self.keyLeft()
  else:
   self.table.refreshMarkers()

 def keyRight(self):
  sel = self.selected
  if sel[0] == 'game':
   new = sel[1] + 1
   if new in self.columns:
    self.select((sel[0], new))
   else:
    self.select(('free',min(self.free)))
  if sel[0] == 'goal':
   new = sel[1] + 1
   if new in self.suits:
    self.select((sel[0], new))
   else:
    self.select(('game', min(self.columns)))
  if sel[0] == 'free':
   new = sel[1] + 1
   if new in self.free:
    self.select((sel[0], new))
   else:
    self.select(('goal', min(self.suits)))
  sel = self.selected
  stack = self.table[sel]
  if len(self.held) == 0 and len(stack) == 0:
   self.keyRight()
  else:
   self.table.refreshMarkers()

# play a game if this script is run
if __name__ == '__main__':
 Game()
