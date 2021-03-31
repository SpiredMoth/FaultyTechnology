import json
import math
import os
import random

import PySimpleGUI as sg


#######  Faulty Technology logic  #######
class FaultyTech:
    # Required defaults for setattr checking
    min = 1
    max = 6

    def __init__(self, swap_min: int = 1, swap_max: int = 1, party_size: int = 1, swapins: bool = False, diff_swaps: bool = False, boxed_pkm: int = 0, shifts: bool = False) -> None:
        # Standard Faulty Tech options
        self.party_size = party_size  # current party size
        self.min        = swap_min    # fewest allowed swaps
        self.max        = swap_max    # most allowed swaps

        # Extra randomization options
        self.boxed      = boxed_pkm   # total pkm currently stored in PC
        self.diff_swaps = diff_swaps  # can withdrawal <= deposited
        self.swapins    = swapins     # randomize Box 1 members to swap in
        self.shifts     = shifts      # randomize box shifts

    def __setattr__(self, name: str, value) -> None:
        if name in ('shifts', 'swapins', 'diff_swaps'):  # Booleans
            value = bool(value)
        else:
            # ???: make sure value is an integer?
            value = int(value)
            if value < 0:
                print(f"Cannot set {name} to a negative number")
                return None
            if name in ('min', 'max', 'party_size') and value > 6:
                print(f"Cannot set '{name}' to '{value}' because it's not a legitimate party size")
                return None
            if name == 'min' and value > self.max:
                print("Cannot set a 'min' to a number greater than 'max'.")
                return None
            elif name == 'max' and value < self.min:
                print("Cannot set a 'max' to a number lower than 'min'.")
                return None
        return super(FaultyTech, self).__setattr__(name, value)

    def get_config(self) -> dict:
        """Return instance attributes in a dict."""
        config = {
            "party_size": self.party_size,
            "min":        self.min,
            "max":        self.max,
            "boxed":      self.boxed,
            "swapins":    self.swapins,
            "shifts":     self.shifts,
            "diff_swaps": self.diff_swaps
        }
        return config

    def from_config(self, config: dict) -> None:
        """Set instance attributes from a dict."""
        for key, value in config.items():
            super(FaultyTech, self).__setattr__(key, value)

    def _pick(self, swap_count, swap_population) -> list:
        """Pick swaps as 1-based slot indices."""
        swaps = random.sample(range(1, swap_population + 1), swap_count)
        return swaps

    def swaps(self) -> list:
        """Generate list of swaps to be made."""
        if self.party_size == 1 and self.boxed == 0:
            print("Cannot make changes to party with only 1 Pokémon.")
            return []
        output = []
        swap_count = min(random.randint(self.min, self.max),
                         self.party_size - int(self.boxed == 0))
        output.append(self._pick(swap_count, self.party_size))

        # if user wants a chance at fewer swap-ins than swap-outs
        if self.diff_swaps:
            # reroll swap_count for new value
            # interval used: [0, swap_count] biased towards swap_count
            swap_count -= round(random.triangular(mode=0) * swap_count)

        if self.swapins and swap_count:
            remaining = min(self.boxed, 30)
            output.append(self._pick(
                min(swap_count, remaining), min(remaining, 30)))

        if self.shifts and self.boxed > 30 and swap_count:
            if not self.swapins:
                output.append([])
            for box in range(1, math.ceil(self.boxed / 30)):
                remaining = self.boxed - 30 * box
                output.append(self._pick(
                    min(swap_count, remaining), min(remaining, 30)))
        return output


#######  PySimpleGUI layout  #######
sg.theme("DarkAmber")
BOX_COUNT = [i for i in range(1, 33)]


def SlotBtn(button_text: str, key_name: str) -> sg.Button:
    return sg.Button(button_text, size=(5, 2), key=key_name, pad=(0, 0), button_color="grey on grey", tooltip="A number means the slot is filled. Click the slot to toggle the number on/off\nAn orange background represent swap to make")


layout_controls = [
    [sg.Text("Config Name:"), sg.Input(key="-CONFIG_NAME-"), sg.Button("Load...", key="Load", disabled=True), sg.Button("Save", key="Save", disabled=True)],
    [
        sg.Text("Minimum number to swap"), sg.Spin((1, 2, 3, 4, 5, 6), key="-MIN-", size=(2, 1), enable_events=True),
        sg.Text("Maximum number to swap"), sg.Spin((1, 2, 3, 4, 5, 6), key="-MAX-", size=(2, 1), enable_events=True)
    ],
    [
        sg.Checkbox("Randomize swap-ins", key="-SWAPINS-", enable_events=True, tooltip="When enabled, box slots will be chosen for you\nto swap into your party"),
        sg.Checkbox("Allow fewer swap-ins", key="-DIFF_SWAPS-", enable_events=True, visible=False, tooltip="When enabled, fewer box slots may be chosen to\nswap in than party slots were chosen to swap out"),
    ],
    [sg.Checkbox("Randomize box swaps", key="-SHIFTS-", enable_events=True, tooltip="When enabled, suggestions will be made for slots\nin later boxes whose contents should be moved\nto fill in gaps in earlier boxes")],
    [sg.Column([[sg.Button("Pick swaps"), sg.Button("Reset")]], justification="center")],
]

party_slots = [[SlotBtn(r*2+c, f"-PARTY_{r*2+c}-") for c in range(1, 3)] for r in range(0, 3)]
box_slots = [[SlotBtn(r*6+c, f"-BOX_{r*6 + c}-") for c in range(1, 7)] for r in range(0, 5)]

box_controls = [
    [
        sg.Text("Box "),
        sg.Spin([1], initial_value=1, enable_events=True, key="-CURRENT_BOX-", size=(3, 1)),
        sg.Text("of"),
        sg.Spin(BOX_COUNT, initial_value=1, enable_events=True, key="-MAX_BOXES-", size=(3, 1))
    ]
]

# TODO: About screen

layout = [
    # [sg.Text("This is just a test window for SpiredMoth's Faulty Technology script")],
    [sg.Column([[sg.Text("Faulty Technology\nRandomized Swaps Tool", justification="center", font=(None, 20))]], justification="center")],
    [sg.Column([[sg.Text("by SpiredMoth", font=(None, 8))]], justification="center")],
    [sg.Column(layout_controls)],
    [
        sg.Column(party_slots, pad=(50, 0)),
        sg.Column(box_controls + box_slots, element_justification="center"),
    ]
]


#######  interface logic  #######
def update_party(config: dict, picks: list = []):
    for i in range(1, 7):
        color = f"{'grey' if i > config['party_size'] else 'black'} on {'orange' if i in picks else 'grey'}"
        window[f"-PARTY_{i}-"].update(button_color=color)


def update_box(config:dict, current_box: int = 1, picks: list = []):
    for i in range(1, 31):
        color = f"{'grey' if i + (current_box - 1) * 30 > config['boxed'] else 'black'} on {'orange' if i in picks else 'grey'}"
        window[f"-BOX_{i}-"].update(button_color=color)


def apply_config(src: dict, dest: dict):
    for k in src:
        dest[k] = src[k]
        if k in ("party_size", "boxed"):
            continue
        window[f"-{k.upper()}-"].update(dest[k])
    boxes, slots = divmod(dest["boxed"], 30)
    max_box = max(boxes + (slots > 0), 1)
    window["-CURRENT_BOX-"].update(values=BOX_COUNT[:max_box], disabled=max_box == 1)
    window["-MAX_BOXES-"].update(value=max_box)
    if dest["swapins"]:
        window["-DIFF_SWAPS-"].update(visible=True)
    else:
        window["-DIFF_SWAPS-"].update(visible=False)
        dest["diff_swaps"] = False
    window["-PARTY_1-"].update(button_color="black on grey")


window = sg.Window("Pokémon Faulty Technology", layout, finalize=True)
window["-PARTY_1-"].update(button_color="black on grey")
win2_active = False

run = FaultyTech()
defaults = run.get_config()
config = run.get_config()
current_box, recent = 1, 0  # TODO: better delay logic?
update_slots = True
swap_list = [[]]

saved_runs = dict()
if os.path.exists("faulty_technology.json"):
    with open("faulty_technology.json", "r", encoding="UTF-8") as f:
        saved_runs = json.loads(f.read())

if len(saved_runs) == 1:
    for k, v in saved_runs.items():
        run.from_config(v)
        apply_config(v, config)
        window["-CONFIG_NAME-"].update(k)
elif len(saved_runs):
    window["Load"].update(disabled=False)


while True:
    config = run.get_config()
    if config["party_size"] + config["boxed"] == 1 or recent > 0:
        window["Pick swaps"].update(disabled=True)
    else:
        window["Pick swaps"].update(disabled=False)

    if update_slots:
        update_party(config, swap_list[0])
        update_box(config, current_box, swap_list[current_box] if len(swap_list) > current_box else [])
        update_slots = False

    event, values = window.read(timeout=500)
    if event == sg.WIN_CLOSED:
        break

    if event == "Load" and not win2_active:
        win2_active = True
        layout_load = [
            [sg.Listbox(values=sorted(list(saved_runs.keys())), enable_events=True, size=(30, 6), key="-SAVES-")],
            [sg.Column([[sg.Button("Select"), sg.Button("Cancel")]], justification="right")]
        ]
        win2 = sg.Window("Load Saved Configuration", layout_load)
    elif event == "Save" and values["-CONFIG_NAME-"]:
        if saved_runs.get(values["-CONFIG_NAME-"], {}) != config:
            saved_runs[values["-CONFIG_NAME-"]] = config
    elif event == "-MIN-":
        if values["-MIN-"] <= config["max"]:
            config["min"] = values["-MIN-"]
        else:
            window["-MIN-"].update(config["min"])
    elif event == "-MAX-":
        if values["-MAX-"] >= config["min"]:
            config["max"] = values["-MAX-"]
        else:
            window["-MAX-"].update(config["max"])
    elif event in ("-SWAPINS-", "-DIFF_SWAPS-", "-SHIFTS-"):
        config[event.lower().strip("-")] = values[event]
        if event == "-SWAPINS-" and not config["swapins"]:
            config["diff_swaps"] = False
            window["-DIFF_SWAPS-"].update(False, visible=False)
        elif event == "-SWAPINS-":
            window["-DIFF_SWAPS-"].update(visible=True)
    elif event == "Reset":
        apply_config(defaults, config)
        swap_list = [[]]
        update_slots = True
        current_box = 1
        window["-CURRENT_BOX-"].update(1)
        if len(saved_runs):
            window["Load"].update(disabled=False)
    elif event.startswith("-PARTY_"):
        target_slot = int(event[7])
        if target_slot == config["party_size"]:
            target_slot = max(1, target_slot - 1)
        config["party_size"] = target_slot
        update_slots = True
    elif event.startswith("-BOX_"):
        target_slot = int(event[5:].strip("-"))
        target_slot -= config["boxed"] == target_slot
        config["boxed"] = target_slot + (current_box - 1) * 30
        update_slots = True
    elif event == "Pick swaps":
        recent = 5
        current_box = 1
        window["-CURRENT_BOX-"].update(1)
        swap_list = run.swaps()
        update_slots = True
    elif event == "-MAX_BOXES-":
        max_box = int(values["-MAX_BOXES-"])
        update_slots = max_box < current_box
        window["-CURRENT_BOX-"].update(values=BOX_COUNT[:max_box], disabled=max_box == 1, value=1 if update_slots else current_box)
        current_box = 1 if update_slots else int(values["-CURRENT_BOX-"])
        config["boxed"] = max_box * 30 if update_slots else config["boxed"]
    elif event == "-CURRENT_BOX-":
        current_box = int(values["-CURRENT_BOX-"])
        update_slots = True

    if win2_active:
        event2, values2 = win2.read()
        if event2 == "Select":
            name = values2["-SAVES-"][0]
            window["-CONFIG_NAME-"].update(name)
            apply_config(saved_runs[name], config)
            current_box = 1
            update_slots = True
            window["Load"].update(disabled=len(saved_runs) == 1)
        if event2 in (sg.WIN_CLOSED, "Select", "Cancel"):
            win2_active = False
            win2.close()

    run.from_config(config)

    if event != "Pick swaps":
        recent -= 1
    if values["-CONFIG_NAME-"]:
        name = values["-CONFIG_NAME-"]
        if saved_runs.get(name, {}) == config:
            window["Save"].update(disabled=True)
        else:
            window["Save"].update(disabled=False)
    else:
        window["Save"].update(disabled=True)


window.close()

if len(saved_runs):
    with open("faulty_technology.json", "w", encoding="UTF-8") as f:
        f.write(json.dumps(saved_runs, indent=4))
