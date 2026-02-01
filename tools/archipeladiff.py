import bsdiff4
result = open("mother_rebuilt.nes", "rb").read()
vanilla = open("mother.nes", "rb").read()
patch = bsdiff4.diff(vanilla, result)
open("basepatch.bsdiff4", "wb").write(patch)

symbols = {}

class Entry(object):
    def __init__(self, start_addr, ogname):
        self.address = start_addr
        self.bank = -1
        self.ogname = ogname


lines = open("linked.txt", "r").readlines()
for line in lines:
    what, addr, name = line.split(" ")
    name = name[1:].strip()
    addr = int(addr, 16)
    if not name.startswith("@AP_"):
        continue

    ap, kind, loc = name.split("_", 2)
    loc = loc.split("__", 1)[0].replace("_", " ")
    if not loc in list(symbols.keys()):
        symbols[loc] = {}

    if not kind in list(symbols[loc].keys()):
        symbols[loc][kind] = []
    symbols[loc][kind].append(Entry(addr, name))

from glob import glob
import os
files = glob("src/global/objects/1/*.asm", recursive=True)
files += glob("src/global/objects/2/*.asm", recursive=True)
files += glob("src/global/objects/3/*.asm", recursive=True)

do_sets = {}

for file in files:
    bank = int(os.path.dirname(file).replace("src/global/objects/", ""))+0xF
    lines = open(file, "r").readlines()
    i = 0
    current_object = ""
    for line in lines:
        if line.find("@AP_") == -1:
            continue

        name = line.strip().split(" ")[0]
        ap, kind, loc = name.split("_", 2)
        loc = loc.split("__", 1)[0].replace("_", " ")
        for entry in symbols[loc][kind]:
            if entry.ogname == name:
                entry.bank = bank

rom_addrs = []
client_addrs = []

for loc in list(symbols.keys()):
    for kind in list(symbols[loc].keys()):
        for entry in symbols[loc][kind]:
            out_loc = loc
            if out_loc.startswith("Sweet s"):
                out_loc = out_loc.replace("Sweet s", "Sweet's")
            elif loc.startswith("Duncan s"):
                out_loc = out_loc.replace("Duncan s", "Duncan's")
            elif loc.startswith("Mt0 Itoi"):
                out_loc = out_loc.replace("Mt0 Itoi", "Mt. Itoi")

            out = f"({hex(entry.bank)}, {hex(entry.address)}): \"{out_loc}\","
            if kind == "ITEMPLACE":
                rom_addrs.append(out)
            else:
                if out_loc.endswith(" X"):
                    for i in range(4):
                        new_out = out.replace("):", f", {i}):").replace(out_loc, out_loc.replace(" X", f" {i+1}"))
                        client_addrs.append(new_out)
                else:
                    client_addrs.append(out)

print("item_place_locations = {")
for a in rom_addrs:
    print("    "+a)
print("}")

print("all_object_codes = {")
for b in client_addrs:
    print("    "+b)
print("}")