# Hide-Furni-v4.0 (Lande original creator)
- Disappear furni from floor or wall, you can rollback only floor furni.
- You must move furni after enabling extension for hide
- some furnis cannot be rollbacked for example LTD furni, consumable furni, and somo specific furni, you will se msg

# Install
python -m pip install g-python

# Commands
:hide on

:hide off
- Enable/disable the extension

:rollback x (x is a number > 0)
- Reappear x furni (only works for floor furni, for wall item you can hide but you must reenter room to reset)
- only works when :hide on (extension enabled)

:hide mute

:hide unmute
- Mute/unmute extension messages for id notification (of each furni hidden) and number of rollback furni
- only works when :hide on (extension enabled)
