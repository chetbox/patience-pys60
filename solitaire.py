"""classic solitaire game

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

cardWidth = cards.cardWidth = 23
cardHeight = cards.cardHeight = 38

class Game:

 def __init__(self, difficulty = 3):
  self.difficulty = difficulty
  self.columns = range(1,8)
  self.suits = range(1,5)
  self.table = Table(initialCards = Deck(visible = False))
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
  # add available cards stacks
  table.addStack(id = ('open',1))
  table[('open',1)].x = 2 + cardWidth * 1.5
  table[('open',1)].cascadeX = 10
  table[('open',1)].cascadeY = 0
  table[('open',1)].drawBase = False
  # add goal stacks
  x = 3 * (cardWidth + 1) + cardWidth / 2
  goal = 0
  for suit in self.suits:
   table.addStack(id = ('goal', suit))
   table[('goal', suit)].x = x
   table[('goal', suit)].y = 1
   table[('goal', suit)].cascadeX = 0
   table[('goal', suit)].cascadeY = 0
   x += cardWidth + 1
  x = cardWidth / 2 + 1
  for col in self.columns:
   table.addStack(id = ('game', col))
   table[('game', col)].x = x
   table[('game', col)].y = 45
   table[('game', col)].cascadeX = 0
   table[('game', col)].cascadeY = 10
   x += cardWidth + 1
   for n in range(col):
    table.moveCards(pile, self.table[('game', col)], 1)
   table[('game', col)][-1].visible = True
  # add temporary cards for held stack
  table.addStack(id = ('held',1))
  table[('held',1)].x = 40
  table[('held',1)].y = 150
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
  if sel[0] == 'game':
   if len(stack[:stack.selectedIndex]) > 0 and stack[stack.selectedIndex - 1].visible:
    self.select(sel, stack.selectedIndex - 1)
  self.table.refreshMarkers()

 def keyDown(self):
  sel = self.selected
  stack = self.table[sel]
  if len(stack[stack.selectedIndex:]) > 1:
   self.select(sel, stack.selectedIndex + 1)
  self.table.refreshMarkers()

 def keySelect(self):
  sel = self.selected
  stack = self.table[sel]
  card = stack.selected()
  pile = self.table[('pile',1)]
  open = self.table[('open',1)]
  if sel[0] == 'game' or sel[0] == 'goal' or sel[0] == 'open':
   # turn over a card if not visible
   if card and not(card.visible) and card == stack[-1] and len(self.held) == 0:
    card.visible = True
    self.table.refresh()
    return
   if len(self.held) > 0:
    # drop cards if possible
    if (sel[0] == 'game' and len(stack) == 0 and int(self.held[0]) == 13) or (len(stack) == 0 and sel[0] == 'goal' and int(self.held[0]) == 1 and len(self.held) == 1) or (sel[0] == 'goal' and len(stack) > 0 and stack[-1].suit() == self.held[0].suit() and int(stack[-1]) - int(self.held[0]) == -1 and len(self.held) == 1) or (stack == self.prevStack) or (sel[0] == 'game' and len(stack) > 0 and int(stack[-1]) - int(self.held[0]) == 1 and stack[-1].colour() != self.held[0].colour()):
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
  # open new cards from pile
  if sel[0] == 'pile' and len(self.held) == 0:
   # hide current open cards
   if len(open) > 0:
    for openCard in open:
     openCard.visible = False
    self.table.moveCards(open, pile, toBottom = True)
   # show new cards
   self.table.moveCards(pile, open, min(len(pile),self.difficulty))
   for openCard in open:
    openCard.visible = True
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
    self.select(('open',1))
  if sel[0] == 'pile':
   self.select(('game', max(self.
columns)))
  if sel[0] == 'open':
   self.select(('pile',1))
  # if no cards open don't select it
  sel = self.selected
  stack = self.table[sel]
  if (sel[0] == 'open' or len(self.held) == 0) and len(stack) == 0:
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
    self.select(('pile',1))
  if sel[0] == 'goal':
   new = sel[1] + 1
   if new in self.suits:
    self.select((sel[0], new))
   else:
    self.select(('game', min(self.columns)))
  if sel[0] == 'open':
   self.select(('goal', min(self.suits)))
  if sel[0] == 'pile':
   self.select(('open',1))
  # if no cards open don't select it
  sel = self.selected
  stack = self.table[sel]
  if (sel[0] == 'open' or len(self.held) == 0) and len(stack) == 0:
   self.keyRight()
  else:
   self.table.refreshMarkers()

# play a game if this script is run
if __name__ == '__main__':
 Game()
