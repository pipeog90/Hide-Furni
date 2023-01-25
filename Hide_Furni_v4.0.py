import re
import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction
from time import sleep

extension_info = {
    "title": "Hide_Furni_v4.0",
    "description": "Hide a furni",
    "version": "4.0",
    "author": "felipeXXI"
}

ext = Extension(extension_info, sys.argv)
ext.start()

furni_id = 0  # Stores furni id
hide_furni = False  # False if Hide Furni is disabled, True if enabled
mute_off = True  # allow the user to turn on or off msg with furni id when removed and msg when rollback
rollback_stock = []  # Stores furni information when removed, so it will be correctly rollback
rollback_range = 0  # Gets number of furni that want to be rollback by user
rollback_count = 0  # Gets the effective number of furni that were rollback
not_rollback_count = 0  # Gets the number of furni that won't be rollback in the room


def commands(message):
    global hide_furni, rollback_range, rollback_count, mute_off, not_rollback_count
    text = message.packet.read_string().lower()

    if text == ":hide on" and hide_furni is True:
        message.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Already ON ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide off" and hide_furni is False:
        message.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Already OFF ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide on" and hide_furni is False:
        message.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => ON ]"}{i:0}{i:31}{i:0}{i:0}')
        hide_furni = True
    if text == ":hide off" and hide_furni is True:
        message.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => OFF ]"}{i:0}{i:31}{i:0}{i:0}')
        hide_furni = False
    if text == ":hide mute" and hide_furni is True:
        message.is_blocked = True
        mute_off = False
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => MUTE ON ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide unmute" and hide_furni is True:
        message.is_blocked = True
        mute_off = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => MUTE OFF  ]"}{i:0}{i:31}{i:0}{i:0}')
    if text.startswith(":rollback"):
        message.is_blocked = True
        try:
            rollback_range = int(text[10:])
        except ValueError:
            return ext.send_to_client(
                '{in:Chat}{i:123456789}{s:"[ Hide furni => Only number available ]"}{i:0}{i:31}{i:0}{i:0}')
        for i in range(rollback_range):
            if rollback_stock:
                rollback()
            else:
                break
        if mute_off:
            ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Rollback ' + str(rollback_count)
                               + ' furni ]"}{i:0}{i:1}{i:0}{i:0}')
            if not_rollback_count > 0:
                ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => ' + str(not_rollback_count)
                                   + ' furni will not rollback ]"}{i:0}{i:1}{i:0}{i:0}')
        rollback_count = 0


def rollback():
    global rollback_stock, rollback_count
    if rollback_stock[0][0] == "floor":
        (item, Id, form, loc1, loc2, loc3, siz1, siz2, fix1, fix2, fix3, fix4, fix5) = rollback_stock[0]
        ext.send_to_client('{in:ObjectAdd}{i:' + str(Id) + '}{i:' + str(form) + "}{i:" + str(loc1) + '}{i:' + str(loc2)
                           + '}{i:' + str(loc3) + '}{s:' + '"' + str(siz1) + '"' + '}{s:' + '"' + str(siz2) + '"'
                           + '}{i:' + str(fix1) + '}{i:' + str(fix2) + '}{s:' + '"' + str(fix3) + '"' + '}{i:' + str(
            fix4)
                           + '}{i:' + str(fix5) + '}{i:0}{s:""}')
        # print('{in:ObjectAdd}{i:' + str(Id) + '}{i:' + str(form) + '}{i:' + str(loc1) + '}{i:' + str(loc2) + '}{i:'
        # + str(loc3) + '}{s:' + '"' + str(siz1) + '"' + '}{s:' + '"' + str(siz2) + '"' + '}{i:' + str(fix1)
        # + '}{i:' + str(fix2) + '}{s:' + '"' + str(fix3) + '"' + '}{i:' + str(fix4) + '}{i:' + str(
        # fix5) + '}{i:0}{s:""}')
        rollback_count += 1
        del rollback_stock[0]
    else:
        (item, Id, form, pos1, fix1, fix2, fix3) = rollback_stock[0]
        ext.send_to_client('{in:ItemAdd}{s:' + '"' + str(Id) + '"' + '}{i:' + str(form) + '}{s:' + '"' + str(pos1)
                           + '"' + '}{s:' + '"' + str(fix1) + '"' + '}{i:' + str(fix2) + '}{i:' + str(
            fix3) + '}{i:0}{s:""}')
        # print('{in:ItemAdd}{s:' + '"' + str(Id) + '"' + '}{i:' + str(form) + '}{s:' + '"' + str(pos1) + '"' + '}{s:'
        # + '"' + str(fix1) + '"' + '}{i:' + str(fix2) + '}{i:' + str(fix3) + '}{i:0}{s:""}')
        rollback_count += 1
        del rollback_stock[0]
    # print(rollback_stock)


def move_objects_floor(packet):
    global furni_id, hide_furni, mute_off

    [furni_id, x, y, z] = packet.packet.read("iiii")

    if hide_furni is True:
        ext.send_to_client('{in:ObjectRemove}{s:"' + str(furni_id) + '"}{b:false}{i:0}{i:0}')
        if mute_off:
            ext.send_to_client(
                '{in:Chat}{i:123456789}{s:"[Furni Id ' + str(furni_id) + ' removed]"}{i:0}{i:30}{i:0}{i:0}')


def move_objects_wall(packet):
    global furni_id, hide_furni, mute_off, not_rollback_count

    [furni_id, x] = packet.packet.read("is")

    if hide_furni is True:
        ext.send_to_client('{in:ItemRemove}{s:"' + str(furni_id) + '"}{b:false}{i:0}{i:0}')
        not_rollback_count += 1
        if mute_off:
            ext.send_to_client(
                '{in:Chat}{i:123456789}{s:"[Furni Id ' + str(furni_id) + ' removed]"}{i:0}{i:30}{i:0}{i:0}')


def get_move_objects_info(packet):
    global furni_id, hide_furni, mute_off, not_rollback_count
    if hide_furni is True:
        #print(packet.packet.read("iiiiissiisiii"))
        (furni_id, form, loc1, loc2, loc3, siz1, siz2, fix1, fix2, fix3, fix4, fix5, fix6) = packet.packet.read("iiiiissiisiii")
        if fix4 == -1:      # Do no stock in rollback furni that causes the extension to crash: LTD furni, staff only furni, etc.
            rollback_stock.insert(0, ["floor", furni_id, form, loc1, loc2, loc3, siz1, siz2, fix1, fix2, fix3, fix4, fix5])
        elif fix4 != -1 and mute_off:
            ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => This specific furni cannot be rollback ]"}{i:0}{i:31}{i:0}{i:0}')
            not_rollback_count += 1
    # print(rollback_stock)


def reset_rollback(packet):
    global rollback_stock, not_rollback_count
    rollback_stock = []  # reset range every time user enters a room
    not_rollback_count = 0


def block_error_message(message):
    global hide_furni
    if hide_furni is True:
        message.is_blocked = True  # hides annoying message that you cannot move furni from rooms

ext.intercept(Direction.TO_SERVER, move_objects_floor, "MoveObject")
ext.intercept(Direction.TO_SERVER, move_objects_wall, "MoveWallItem")
ext.intercept(Direction.TO_CLIENT, get_move_objects_info, "ObjectUpdate")
ext.intercept(Direction.TO_SERVER, commands, "Chat")
ext.intercept(Direction.TO_CLIENT, reset_rollback, "RoomEntryTile")
ext.intercept(Direction.TO_CLIENT, block_error_message, "NotificationDialog")
