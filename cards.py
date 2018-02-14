"""playing card drawing library for PyS60

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


# global options
cardWidth = 23
cardHeight = 38
tableColour = 0x007700
markerWidth = 9
markerHeight = 9
markerColour = 0x777777
markerBorderColour = 0x999999


from random import shuffle, randrange
from appuifw import app, Canvas
from graphics import Image, ROTATE_180
from e32 import ao_yield

class Deck:

 def __init__(self, visible=False):
  self._colours = [
   0x000000,
   0xff0000,
  ]
  self._suits = [
   {'value':u'\u2660','colour':self._colours[0]},
   {'value':u'\u2663','colour':self._colours[0]},
   {'value':u'\u2666','colour':self._colours[1]},
   {'value':u'\u2665','colour':self._colours[1]},
  ]
  self._values = []
  # use this if aces are high:
  #for value in range(2,15):
  # if (value == 14):
  # use this if aces are low:
  for value in range(1,14):
   if (value == 1):
    self._values += [{'value':value, 'name':'A'}]
   elif (value == 13):
    self._values += [{'value':value, 'name':'K'}]
   elif (value == 12):
    self._values += [{'value':value, 'name':'Q'}]
   elif (value == 11):
    self._values += [{'value':value, 'name':'J'}]
   else:
    self._values += [{'value':value, 'name':str(value)}]
  self.cards = self._createDeck(self._values, self._suits, visible = visible)

 def _createDeck(self, values, suits, visible = False):
  cards = []
  for suit in suits:
   for value in values:
    cards += [Card(value, suit, self, visible = visible)]
  return cards

 def __call__(self):
  return self.cards

 def __getitem__(self, index):
  return self.cards[index]

 def __getslice__(self, index1, index2):
  return self.cards[index1:index2]

 def __len__(self):
  return len(self.cards)

 def shuffle(self):
  shuffle(self.cards)

 def cut(self):
  pos = randrange(len(self.cards))
  self.cards = self.cards[pos:] + self.cards[:pos]

 def sort(self):
  self.cards.sort()

class Card:

 def __init__(self,
  value, suit, deck,
  visible = True,
  bgColour = 0xffffff,
  borderColour = 0x000000,
  patternColour1 = (0,0,255),
  patternColour2 = (150,150,255)
 ):
  if (value in deck._values):
   self._value = value
   if (suit in deck._suits):
    self._suit = suit
   else:
    raise 'Invalid suit:', str(suit)
  else:
   raise 'Invalid value:', str(value)
  self.visible = visible
  # look & feel:
  self.bgColour = bgColour
  self.borderColour = borderColour
  self.patternColour1 = patternColour1
  self.patternColour2 = patternColour2
  self.image = None
  self.imageHidden = None

 def getImage(self):
  if self.visible:
   if not(self.image):
    self.image = self.genImage()
   return self.image
  else:
   if not(self.imageHidden):
    self.imageHidden = self.genImage()
   return self.imageHidden

 def genImage(self):
  img = Image.new((cardWidth,cardHeight))
  img.rectangle(
   (0,0,cardWidth,cardHeight),
   self.borderColour,
   self.bgColour
  )
  if self.visible:
   txtimg = Image.new((cardWidth - 2,cardHeight / 2 - 1))
   txtimg.rectangle(
    (0,0,cardWidth - 2,cardHeight / 2 - 1),
    self.bgColour,
    self.bgColour
   )
   txtimg.text(
    (1, 8),
    unicode(self.name()),
    self.colour(),
    u'fixed6x10'
   )
   img.blit(txtimg,target=(1,1))
   img.blit(txtimg.transpose(ROTATE_180),target=(1,cardHeight / 2 + 1))
  else:
   repeat = 4
   for top in range(0,repeat):
    img.ellipse([(cardWidth /3,cardHeight *(top*2+1)/(repeat*2+2)),(cardWidth *2/3,cardHeight *(top*2+3)/(repeat*2+2))], self.patternColour1, self.patternColour2)
  return img

 def __int__(self):
  return self._value['value']

 def name(self):
  return self._value['name'] + self._suit['value']

 def colour(self):
  return self._suit['colour']

 def suit(self):
  return self._suit['value']

 def value(self):
  return self._value['name']

 def putOn(self, stack):
  return stack.addCard(self)

 def takeOff(self, stack):
  return stack.removeCard(self)


class Stack:

 def __init__(
  self,
  initialCards = [],
  cascadeX = 0,
  cascadeY = 12,
  id = None,
  x = 1 + cardWidth / 2,
  y = 1,
  selectedIndex = None,
  drawBase = True
 ):
  self._cards = initialCards[:]
  self.cascadeX = cascadeX
  self.cascadeY = cascadeY
  self.id = id
  self.x = x
  self.y = y
  self.selectedIndex = selectedIndex
  self.image = None
  self.drawBase = drawBase

 def getImage(self):
  if self.drawBase:
   if not(self.image):
    self.image = self.genImage()
   return self.image
  else:
   return None

 def genImage(self):
  img = Image.new((cardWidth,cardHeight))
  img.rectangle(
   (0,0,cardWidth,cardHeight),
   0x000000,
   tableColour
  )
  return img

 def selected(self):
  if self.selectedIndex and len(self._cards):
   return self._cards[self.selectedIndex]
  return None

 def __call__(self):
  return self._cards

 def __getitem__(self, index):
  return self._cards[index]

 def __getslice__(self, index1, index2):
  return self._cards[index1:index2]

 def __len__(self):
  return len(self._cards)

 def index(self, index):
  return self._cards.index(index)

 def addCard(self, card):
  if not(card in self._cards):
   self._cards.append(card)

 def removeCard(self, card):
  if (card in self._cards):
   self._cards.remove(card)

 def remove(self, number):
  output = self._cards[(-number):]
  self._cards = self._cards[0:(-number)]
  return output

 def add(self, cards, toBottom = False):
  if toBottom:
   self._cards = cards + self._cards
  else:
   self._cards += cards

 def cards(self):
  return self._cards

 def putOn(self, table):
  return table.addStack(self)

 def shuffle(self):
  shuffle(self._cards)


class Table:

 def __init__(self, initialCards = None, cascadeX = 0, cascadeY = 0, visible = False):
  self._defaultCascadeX = cascadeX
  self._defaultCascadeY = cascadeY
  self._defaultVisible = visible
  self._stacks = {}
  if initialCards:
   self._stacks[('pile', 1)] = (Stack(initialCards = initialCards, cascadeX = cascadeX, cascadeY = cascadeY))
  else:
   self._stacks[('pile', 1)] = Stack(initialCards = Deck(visible = visible).cards, cascadeX = cascadeX, cascadeY = cascadeY)
  self._screen = None

 def __call__(self):
  return self._stacks

 def show(self):
  if (self._screen == None):
   self._screen = Screen(self)
  self._screen.start()
  self.width = self._screen.width
  self.height = self._screen.height

 def refresh(self):
  if self._screen:
   self._screen.redraw()

 def refreshMarkers(self):
  if self._screen:
   self._screen.drawMarkers()

 def unshow(self):
  if self._screen:
   self._screen.stop()

 def __getitem__(self, index):
  if index.__class__ == int:
   return self._stacks[self._stacks.keys()[index]]
  else:
   return self._stacks[index]

 def __len__(self):
  return len(self._stacks)

 def addStack(self, id):
  self._stacks[id] = Stack()

 def removestack(self, stack):
  if (stack in self._stacks):
   self._stacks.remove(stack) # convert to dict

 def stacks(self):
  return self._stacks.values()

 def moveCard(self, fromStack, toStack):
  moveCards(1, fromStack, toStack)

 def moveCards(self,fromStack, toStack, number = None, toBottom = False):
  if number:
   toStack.add(fromStack.remove(number), toBottom)
  else:
   toStack.add(fromStack.remove(len(fromStack)), toBottom)


class Screen:

 def __init__(self, table, event_callback = None):
  self._table = table
  self.rightHanded = True
  self.borderSize = 5
  self._screen = Canvas(
  event_callback = event_callback,
   redraw_callback = self.updateScreen
  )
  self._image = None
  self.markerImage = None

 def __call__(self):
  return self._screen

 def start(self):
  app.screen = 'full'
  self._oldScreen = app.body
  app.body = self()
  ao_yield()
  self._image = Image.new(self._screen.size)
  self.width = self._screen.size[0]
  self.height = self._screen.size[1]
  self.redraw()

 def stop(self):
  app.body = self._oldScreen

 def redraw(self,rect=None):
  if self._image:
   self._image.clear(tableColour)
   for stack in self._table:
    self.drawStack(stack)
    x = stack.x
    y = stack.y
    for card in stack:
     self.drawCard((x,y),card)
     x += stack.cascadeX
     y += stack.cascadeY
   # save a copy with no markers
   self._oldImage = self._image
   self.drawMarkers()

 def updateScreen(self,rect=None):
  if self._image:
   self._screen.blit(self._image)
   ao_yield()

 def drawStack(self,stack):
  img = stack.getImage()
  if img:
   self._image.blit(img
,target=(stack.x - cardWidth / 2,stack.y))

 def drawCard(self,(x,y),card):
  self._image.blit(card.getImage()
,target=(x - cardWidth / 2,y))

 def drawMarkers(self):
  if self._oldImage:
   # use a copy of image without markers
   self._image = self._oldImage.new(self._image.size)
   self._image.blit(self._oldImage,target=(0,0))
   for stack in self._table:
    x = stack.x
    y = stack.y
    if stack.selectedIndex and len(stack) <= 0:
     self.drawMarker((x,y))
    for card in stack:
     if stack.selected() == card:
      self.drawMarker((x,y))
     x += stack.cascadeX
     y += stack.cascadeY
   self.updateScreen()

 def drawMarker(self,(x,y)):
  overlap = 4
  self._image.polygon(
   [
    (
     x - overlap + cardWidth / 2,
     y + markerHeight / 2
    ),
    (
     x - overlap + cardWidth / 2 + markerWidth,
     y
    ),
    (
     x - overlap + cardWidth / 2 + markerWidth,
     y + markerHeight
    )
   ],
   markerBorderColour,
   markerColour
  )





