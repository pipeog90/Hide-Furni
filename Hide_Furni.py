import sys
from g_python.gextension import Extension
from g_python.hmessage import Direction

extension_info = {
    "title": "Hide_Furni",
    "description": "Hide a furni",
    "version": "5.0",
    "author": "felipeXXI"
}

ext = Extension(extension_info, sys.argv)
ext.start()

hide_furni = False  # False if Hide Furni is disabled, True if enabled
mute_off = True  # allow the user to turn on or off msg with furni id when removed and msg when rollback
rollback_stock = []  # Stores furni information when removed, so it will be correctly rollback
text = packet = ''
rollback_range = rollback_count = not_rollback_count = furni_id = 0  # Gets number of furni that want to be rollback by user # Gets the effective number of furni that were rollback # Gets the number of furni that won't be rollback in the room # Stores furni id


def text_commands():
    global text, packet, hide_furni, rollback_range, rollback_count, mute_off, not_rollback_count
    text = text.lower()
    if text == ":hide on" and hide_furni is True:
        packet.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Already ON ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide off" and hide_furni is False:
        packet.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Already OFF ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide on" and hide_furni is False:
        packet.is_blocked = hide_furni = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => ON ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide off" and hide_furni is True:
        packet.is_blocked = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => OFF ]"}{i:0}{i:31}{i:0}{i:0}')
        hide_furni = False
    if text == ":hide mute" and hide_furni is True:
        packet.is_blocked = True
        mute_off = False
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => MUTE ON ]"}{i:0}{i:31}{i:0}{i:0}')
    if text == ":hide unmute" and hide_furni is True:
        packet.is_blocked = mute_off = True
        ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => MUTE OFF  ]"}{i:0}{i:31}{i:0}{i:0}')
    if text.startswith(":rollback") and hide_furni is True:
        packet.is_blocked = True
        try:
            rollback_range = int(text[10:])
            for i in range(rollback_range):
                if rollback_stock:
                    rollback()
                else:
                    break
            if mute_off:
                if rollback_count > 0:
                    ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Rollback ' + str(rollback_count) + ' furni ]"}{i:0}{i:1}{i:0}{i:0}')
                if not_rollback_count > 0:
                    ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => ' + str(not_rollback_count) + ' furni will not rollback ]"}{i:0}{i:1}{i:0}{i:0}')
            rollback_count = 0
            not_rollback_count = 0
        except ValueError:
            return ext.send_to_client('{in:Chat}{i:123456789}{s:"[ Hide furni => Only number available ]"}{i:0}{i:31}{i:0}{i:0}')


def chat(message):
    global text, packet
    packet = message
    text = message.packet.read_string().encode('ISO-8859-1').decode('utf-8')
    text_commands()


def whisper(message):
    global text, packet
    packet = message
    text = message.packet.read_string().encode('ISO-8859-1').decode('utf-8').split(' ', 1)[1]
    text_commands()


def send_msg(message):
    global text, packet
    packet = message
    (Id, text) = message.packet.read('is')
    text = text.encode('ISO-8859-1').decode('utf-8')
    text_commands()


def rollback():
    global rollback_stock, rollback_count, not_rollback_count
    ushort = '{' + '}{'.join(rollback_stock[0]) + '}'
    ext.send_to_client(ushort)
    if rollback_stock[0][0] == 'in:ObjectAdd':
        rollback_count += 1
    elif rollback_stock[0][0] == 'in:ItemAdd':
        not_rollback_count += 1
    del rollback_stock[0]


def room_entry_tile(pack):
    global rollback_stock, not_rollback_count, rollback_count
    rollback_stock = []  # reset range every time user enters a room
    not_rollback_count = rollback_count = 0


def notification_dialog(pack):
    global hide_furni
    if hide_furni is True:
        pack.is_blocked = True  # hides annoying message that you cannot move furni from rooms


def move_wall_item(pack):
    global hide_furni, rollback_stock, mute_off
    if hide_furni:
        ushort = pack.packet.g_expression(ext) + '{s:""}{i:-1}{i:0}{i:0}{s:""}'
        ushort = ushort[1:-1].split('}{')
        id_ = pack.packet.read('i')[0]
        ext.send_to_client('{in:ItemRemove}{s:"' + str(id_) + '"}{i:0}')
        if mute_off:
            ext.send_to_client('{in:Chat}{i:123456789}{s:"[Furni id: ' + str(id_) + ' removed]"}{i:0}{i:32}{i:0}{i:0}')
        ushort[0] = 'in:ItemAdd'
        ushort.insert(2, 'i:3')
        ushort[1] = 's:"' + str(id_) + '"'
        rollback_stock.insert(0, ushort)


def move_object(pack):
    global furni_id
    furni_id = pack.packet.read('i')[0]


def object_update(pack):
    global hide_furni, rollback_stock, mute_off, furni_id
    id_ = pack.packet.read('i')[0]
    if hide_furni and id_ == furni_id:
        furni_id = 0
        ushort = pack.packet.g_expression(ext) + '{s:""}'
        ushort = ushort[1:-1].split('}{')

        ext.send_to_client('{in:ObjectRemove}{s:"' + str(id_) + '"}{b:false}{i:0}{i:0}')
        if mute_off:
            ext.send_to_client('{in:Chat}{i:123456789}{s:"[Furni id: ' + str(id_) + ' removed]"}{i:0}{i:30}{i:0}{i:0}')
        ushort[0] = 'in:ObjectAdd'
        rollback_stock.insert(0, ushort)

ext.intercept(Direction.TO_SERVER, move_wall_item, "MoveWallItem")
ext.intercept(Direction.TO_SERVER, move_object, "MoveObject")
ext.intercept(Direction.TO_CLIENT, object_update, "ObjectUpdate")
ext.intercept(Direction.TO_SERVER, chat, "Chat")
ext.intercept(Direction.TO_SERVER, chat, "Shout")
ext.intercept(Direction.TO_SERVER, whisper, "Whisper")
ext.intercept(Direction.TO_SERVER, send_msg, "SendMsg")
ext.intercept(Direction.TO_CLIENT, room_entry_tile, "RoomEntryTile")
ext.intercept(Direction.TO_CLIENT, notification_dialog, "NotificationDialog")
