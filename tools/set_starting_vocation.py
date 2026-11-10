#!/usr/bin/env python3
"""Experimental DQIX first-vocation save patcher. Only creates a separate save.

This is a provisional bridge, not the final in-game vocation-selection screen.
Offsets and IDs based on the open-source DQIX save editor (DQIX/editor).
"""
import argparse
from pathlib import Path
import sys
import zlib

SLOT_SIZE = 32768
FILE_SIZE = 65536
MAGIC = b'DRAGON QUEST IX'
CHECKS = ((16, 20, 36), (36, 40, 132), (132, 136, 28644))
VOCATIONS = {"warrior": 1, "priest": 2, "mage": 3,
            "martial-artist": 4, "thief": 5, "minstrel": 6}
CHARACTER_OFFSET = 136
CHARACTER_SIZE = 572
CURRENT_VOCATION = 80
LEVELS = 2
EXPS = 28
STANDBY_COUNT = 7572
PARTY_COUNT = 7577
SAVE_EXISTS = 21


class SaveError(ValueError):
    pass


def u32(data, offset):
    return int.from_bytes(data[offset:offset + 4], 'little')


def checksums_ok(data):
    return all(u32(data, offset) == zlib.crc32(data[start:end])
               for offset, start, end in CHECKS)


def rewrite_checksums(data):
    for offset, start, end in CHECKS:
        data[offset:offset + 4] = zlib.crc32(data[start:end]).to_bytes(4, 'little')


def patch_save(raw, vocation, slot=0):
    if len(raw) != FILE_SIZE:
        raise SaveError('Expected a 65,536-byte DQIX .sav file')
    if raw[:len(MAGIC)] != MAGIC:
        raise SaveError('Save header is not DRAGON QUEST IX')
    if vocation not in VOCATIONS:
        raise SaveError('Unsupported starting vocation')
    if slot not in (0, 1):
        raise SaveError('Save slot must be 0 or 1')

    data = bytearray(raw)
    # Validate both slots before doing any work, as the original editor does.
    for i in (0, 1):
        base = i * SLOT_SIZE
        if not checksums_ok(data[base:base + SLOT_SIZE]):
            raise SaveError(f'Save slot {i} has invalid checksums; no changes made')

    # Only a baseline from the mandatory early fight is supported.
    # Both save slots must be consistent; otherwise refuse to guess which
    # slot the game will load and leave the original untouched.
    target_id = VOCATIONS[vocation]
    if target_id == VOCATIONS['minstrel']:
        raise SaveError('Choose a different vocation from Minstrel')

    for slot_index in (0, 1):
        base = slot_index * SLOT_SIZE
        buf = data[base:base + SLOT_SIZE]
        if not buf[SAVE_EXISTS] & 1:
            raise SaveError(f'Save slot {slot_index} does not contain a character')
        standby, party = buf[STANDBY_COUNT], buf[PARTY_COUNT]
        if standby > 8 or party != 1 or standby + party > 13:
            raise SaveError('Unsupported character party layout')
        hero = CHARACTER_OFFSET + CHARACTER_SIZE * standby
        current = buf[hero + CURRENT_VOCATION]
        if current != VOCATIONS['minstrel']:
            raise SaveError(f'Expected Minstrel (ID 6), found ID {current}')
        current_level = buf[hero + LEVELS + current]
        current_exp = u32(buf, hero + EXPS + current * 4)
        if current_level != 1 or current_exp not in (0, 7):
            raise SaveError('Only untouched level-1 saves (0 or mandatory 7 EXP) are supported')
        if buf[hero + LEVELS + target_id] != 1 or u32(buf, hero + EXPS + target_id * 4) != 0:
            raise SaveError('Target vocation does not have untouched level-1 state')
        buf[hero + CURRENT_VOCATION] = target_id
        rewrite_checksums(buf)
        data[base:base + SLOT_SIZE] = buf
        if not checksums_ok(data[base:base + SLOT_SIZE]):
            raise SaveError('Internal checksum verification failed')
    return bytes(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Original copied dqix.sav (never overwritten)')
    parser.add_argument('vocation', choices=sorted(VOCATIONS))
    parser.add_argument('--slot', type=int, choices=[0, 1], default=None,\n                        help='Deprecated: both slots are safely updated together')
    parser.add_argument('--output', type=Path, help='Separate output .sav path')
    args = parser.parse_args(argv)
    destination = args.output or args.input.with_name(args.input.stem + '-' + args.vocation + '.sav')
    try:
        if args.input.resolve() == destination.resolve():
            raise SaveError('Refusing to overwrite the input save')
        if destination.exists():
            raise SaveError('Output already exists; refusing to overwrite it')
        modified = patch_save(args.input.read_bytes(), args.vocation)
        with destination.open('xb') as f:
            f.write(modified)
    except (OSError, SaveError) as error:
        parser.exit(1, f'Error: {error}\n')
    print(f'Created: {destination}')
    print('Experimental only: keep your original save and verify stats/equipment in game.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
