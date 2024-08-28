#!/usr/bin/env python3
# %%
import os
import os.path
import re
import shutil

dirname = ""
matched_exts = [".xml", ".lua"]

ignored_files = []

ignored_prefix_patterns = [
    "-",
    " - ",
    " -",
    "interval = ",
    "chance = ",
    "minDamage = ",
    "maxDamage = ",
    "maxDamage = -",
    "speedChange = ",
    "speedChange = -",
    "duration = ",
    "monster.raceId = ",
    "totalDamage = ",
    "lookType = ",
    "monster.speed = ",
    "monster.experience = ",
    "monster.health = ",
    "monster.maxHealth = ",
    "SecondUnlock = ",
    "toKill = ",
    "monster.manaCost = ",
    "runHealth = ",
    "outfitItem = ",
    '<attribute key="duration" value="',
    '<attribute key="leveldoor" value="',
    '<attribute key="weight" value="',
    '<attribute key="ticks" value="',
    '<attribute key="count" value="',
    '<attribute key="damage" value="',
    '<attribute key="charges" value="',
    '<attribute key="armor" value="',
    '<attribute key="defense" value="',
    '<attribute key="attack" value="',
    '<attribute key="maxHitChance" value="',
    '<attribute key="healthTicks" value="',
    '<attribute key="manaTicks" value="',
    '<attribute key="range" value="',
    '<attribute key="healthGain" value="',
    '<attribute key="manaGain" value="',
    '<attribute key="speed" value="',
    '<attribute key="levelDoor" value="',
    '<attribute key="maxtextlen" value="',
    '<attribute key="writeonceitemid" value="',
    '<attribute key="criticalhitdamage" value="',
    '<attribute key="fromDamage" value="',
    '<attribute key="toDamage" value="',
    '<attribute key="level" value="',
]
ignored_line_regexes = []

ignored_ids = []

regex = re.compile(r"\b([1-9][0-9]{2,4})\b")

processed_files = []
replacemap = {}
with open("cid_sid_mapping.txt", "r") as fi:
    for line in fi:
        line = line.strip()
        sid, cid = line.split(",")
        replacemap[sid] = cid
# %%
for root, dirs, files in os.walk(dirname):
    for file in files:
        for ext in matched_exts:
            if file.endswith(ext):
                fullname = root + os.sep + file
                for ignored in ignored_files:
                    if fullname.endswith(ignored):
                        break
                else:
                    processed_files.append(root + os.sep + file)

# %%
for file in processed_files:
    with open(file, "r") as fi, open(file + ".tmp", "w") as fo:
        i = 0
        for line in fi:
            offset = 0
            skipLine = False
            for ignore_regex in ignored_line_regexes:
                if type(ignore_regex) is list:
                    if ignore_regex[0].match(file):
                        ignore_regex = ignore_regex[1]
                    else:
                        continue
                if ignore_regex.match(line):
                    skipLine = True
                    break
            if skipLine:
                fo.write(line)
                continue
            outline = line
            i += 1
            matches = regex.finditer(line)
            skipPosition = 0
            for match in matches:
                skipMatch = False
                if skipPosition > 0:
                    skipPosition -= 1
                    skipMatch = True
                for prefix in ignored_prefix_patterns:
                    if type(prefix) is list:
                        if prefix[0].match(file):
                            prefix = prefix[1]
                        else:
                            continue
                    if match.start() >= len(prefix):
                        if line[match.start() - len(prefix) : match.start()] == prefix:
                            skipMatch = True
                            break
                id = int(match.group())
                # Skip common numbers for intervals and values
                if id in ignored_ids:
                    skipMatch = True
                # Detect positions starting at 30000 < X < 35000
                if id > 30000 and id < 35000:
                    if line[match.start() - 1] == "(":
                        skipPosition = 2
                        skipMatch = True
                if not skipMatch and match.group() in replacemap:
                    print(
                        "{}:{}[{}] - match {} in '{}'".format(
                            file, i, match.start(), match.group(), line
                        )
                    )
                    print(
                        "replacing {} with {}".format(
                            match.group(), replacemap[match.group()]
                        )
                    )
                    outline = (
                        outline[: match.start() + offset]
                        + replacemap[match.group()]
                        + outline[match.end() + offset :]
                    )
                    offset += len(replacemap[match.group()]) - len(match.group())
            fo.write(outline)
    shutil.move(file + ".tmp", file)
    # os.remove(file+'.tmp')
