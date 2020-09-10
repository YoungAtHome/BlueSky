#!/usr/bin/env python3
from bluedot.btcomm import BluetoothClient
from datetime import datetime
from time import sleep
from signal import pause

moving = False
import skywriter

BD_PROTOCOL_VERSION = 1

# robot runs the bluedot server
bd_server = 'artipi'
#bd_server = 'BlueZ 5.43'

"""
[operation],[x],[y]\n

operation is either 0, 1 or 2:
 0 released
 1 pressed
 2 pressed position moved

x & y specify the position on the Blue Dot that was pressed, released and/or moved
Positions are values between -1 and +1, with 0 being the centre and 1 being the radius
of the Blue Dot
x is the horizontal position where +1 is far right
y is the horizontal position where +1 is the top
\n represents the ascii new-line character (ASCII character 10)
"""
bd_release = 0
bd_press = 1
bd_hold = 2

ox = 1
oy = 1
oz = 1

pressed = False

sky_centre = 'center'
direction = {'north': (0, 1), 'east': (1, 0), 'south': (0, -1), 'west': (-1, 0), sky_centre: (0, 0)}

def command(operation, bdx, bdy):
  global pressed
  bd_command = '{},{:.3f},{:.3f}\n'
  print('op={} x={:.3f} y={:.3f}'.format(operation, bdx, bdy))
  if operation == bd_release:
    if not pressed: 
      return
    pressed = False
  print('op={} x={:.3f} y={:.3f}'.format(operation, bdx, bdy))
  c.send(bd_command.format(operation, bdx, bdy))


def data_received(data):
    print("recv - {}".format(data))

print("Connecting to {}".format(bd_server))
c = BluetoothClient(bd_server, data_received)
print("Sending protocol version")
c.send("3,{},BlueSky\n".format(BD_PROTOCOL_VERSION))
print("  Connected to {}".format(bd_server))

#print("Sending")
#try:
#    while True:
#        c.send("hi {} \n".format(str(datetime.now())))
#        sleep(1)
#finally:
#    c.disconnect()
#pause()

some_value = 5000

@skywriter.move()
def move(x, y, z):
  global moving
  global ox, oy, oz
  global pressed
  if moving:
    #print('ignore move')
    return
  moving = True
  #print('pressed={}'.format(pressed))
  # act on material differences only
  if abs(ox-x) > 0.05 or abs(oy-y) > 0.05 or abs(oz-z) > 0.05:
    #print('ox={:.3f} oy={:.3f} oz={:.3f}'.format(x, y, z))
    #print(' x={:.3f}  y={:.3f}  z={:.3f}'.format(x, y, z))
    if z < 0.75:
      if pressed:
        # send hold
        command(bd_hold, (x-0.5)*2, (y-0.5)*2)
      else: #if not pressed:
        pressed = True
        # send press
        command(bd_press, (x-0.5)*2, (y-0.5)*2)
    else:
        # more than 75% up so release
        command(bd_release, (x-0.5)*2, (y-0.5)*2)
    #print('updating ox, oy, oz')
    ox = x
    oy = y
    oz = z
  #print('moving to False')
  moving = False

#@skywriter.flick()
def flick(start,finish):
  print('Got a flick!', start, finish)
  bdx, bdy = direction[start]
  # force finish as opposite direction to start
  bdxf, bdyf = -bdx, -bdy
  #bdxf, bdyf = direction[finish]
  ra = bdx if bdx else bdy
  rb = bdxf if bdxf else bdyf
  
  print('ra={}, rb={}, rb/10={}'.format(ra, rb, rb/10))
  if start=='north' or start=='south':
    command(bd_press, 0, ra)
    for bdyn in range(ra*10, rb*10, rb):
      command(bd_hold, 0, bdyn/10)
    command(bd_release, 0, rb)
  elif start=='east' or start=='west':
    command(bd_press, ra, 0)
    for bdxn in range(ra*10, rb*10, rb):
      command(bd_hold, bdxn/10, 0)
    command(bd_release, rb, 0)

#@skywriter.airwheel()
def spinny(delta):
  global some_value
  some_value += delta
  if some_value < 0:
  	some_value = 0
  if some_value > 10000:
    some_value = 10000
  print('Airwheel:', some_value/100)

#@skywriter.double_tap()
def doubletap(position):
  print('Double tap!', position)
  bdx, bdy = direction[position]
  command(bd_press, bdx, bdy)
  command(bd_release, bdx, bdy)
  command(bd_press, bdx, bdy)
  command(bd_release, bdx, bdy)

@skywriter.tap()
def tap(position):
  print('Tap!', position)
  bdx, bdy = direction[position]
  if position == sky_centre:
    command(bd_release, bdx, bdy)
  else:
    command(bd_press, bdx, bdy)

@skywriter.touch()
def touch(position):
  print('Touch!', position)
  bdx, bdy = direction[position]
  if position == sky_centre:
    command(bd_release, bdx, bdy)
  else:
    command(bd_press, bdx, bdy)


try:
  pause()
finally:
  c.disconnect()
