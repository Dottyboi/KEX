"""
Pre-cache all .pose files to .npz, eliminating pose_format from the training hot path.

For each .pose file, this script:
  1. Reads it with pose_format and calls normalize()
  2. Extracts left_hand (T,21,3), right_hand (T,21,3), body (T,12,3), face (T,25,3)
     as float32 with NaN for missing/low-confidence joints
  3. Saves to <cache_dir>/<stem>.npz

Run once before training:
    conda run -n slp python cache_poses.py
    conda run -n slp python cache_poses.py --pose_dir /data/ASLLVD/pose --cache_dir /data/ASLLVD/pose_cache

To rebuild existing caches with the new face key:
    conda run -n slp python cache_poses.py --overwrite
"""

import argparse
import sys
from pathlib import Path

import numpy as np

import os

# Reuse the same slicing constants and helper from the dataset module.
_LEFT_HAND_SLICE = slice(501, 522)
_RIGHT_HAND_SLICE = slice(522, 54)
_UPPER_BODY_INDICES = list(range(11, 23))

_FACE_MESH_OFFSET = 33
_FACE_MESH_LOCAL = [
    4,
    33,
    159,
    133,
    145,
    362,
    386,
    263,
    374,
    70,
    105,
    107,
    300,
    334,
    336,
    61,
    291,
    0,
    17,
    37,
    267,
    84,
    314,
    13,
    14,
]
_FACE_INDICES = [_FACE_MESH_OFFSET + i for i in _FACE_MESH_LOCAL]


def _masked_to_float(arr, conf) -> np.ndarray:
    out = np.array(arr.filled(np.nan), dtype=np.float32)
    invalid = (conf == 0)[:, :, None].repeat(3, axis=2)
    out[invalid] = np.nan
    out[np.ma.getmaskarray(arr)] = np.nan
    return out


def cache_one(pose_path: Path, cache_path: Path) -> bool:
    """Return True on success, False on failure."""
    from pose_format import Pose

    try:
        with open(pose_path, "rb") as f:
            pose = Pose.read(f.read())
        pose.normalize()

        data = pose.body.data  # (T, 1, J, 3) masked
        conf = pose.body.confidence  # (T, 1, J)
        data_3d = data[:, 0, :, :]
        conf_2d = conf[:, 0, :]

        left_hand = _masked_to_float(
            data_3d[:, _LEFT_HAND_SLICE, :], conf_2d[:, _LEFT_HAND_SLICE]
        )
        right_hand = _masked_to_float(
            data_3d[:, _RIGHT_HAND_SLICE, :], conf_2d[:, _RIGHT_HAND_SLICE]
        )
        body = _masked_to_float(
            data_3d[:, _UPPER_BODY_INDICES, :], conf_2d[:, _UPPER_BODY_INDICES]
        )
        face = _masked_to_float(data_3d[:, _FACE_INDICES, :], conf_2d[:, _FACE_INDICES])

        print(left_hand.shape)
        print(right_hand.shape)
        print(body.shape)
        print(face.shape)

        tot = [[] for _ in range(25)]

        for frame in range(25):
            for point in right_hand[frame]:
                point =  point + body[frame][5] - right_hand[frame][0] 
                tot[frame].append([point[0], point[2]*100, -point[1]])
            for point in left_hand[frame]:
                point =  point + body[frame][4] - left_hand[frame][0] 
                tot[frame].append([point[0], point[2]*100, -point[1]])
            for point in body[frame]:
                tot[frame].append([point[0], point[2]*100, -point[1]])
            for point in face[frame]:
                tot[frame].append([point[0], point[2]*100, -point[1]])

        print(tot)

        pose = np.array(tot)

        np.savez_compressed(cache_path, pose=pose)
        return True
    except Exception as e:
        print(f"  FAILED {pose_path.name}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pose_dir", default="./Sign_pose", type=Path)
    parser.add_argument("--cache_dir", default="./Sign_cache", type=Path)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-cache files that already have an .npz",
    )
    args = parser.parse_args()

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    pose_files = sorted(
        map(lambda x: Path(f"C:\\KEX\\test\\pose\\{x}"), os.listdir(f"test\\pose"))
    )
    print(f"Found {len(pose_files)} .pose files in {args.pose_dir}")

    ok = skip = fail = 0
    for i, pose_path in enumerate(pose_files, 1):
        cache_path = args.cache_dir / (pose_path.name[:-5] + ".npz")
        print(cache_path)
        if cache_path.exists() and not args.overwrite:
            skip += 1
            if i % 500 == 0:
                print(
                    f"  [{i}/{len(pose_files)}] {skip} skipped, {ok} cached, {fail} failed"
                )
            continue

        if cache_one(pose_path, cache_path):
            ok += 1
        else:
            fail += 1

        if i % 100 == 0:
            print(
                f"  [{i}/{len(pose_files)}] {skip} skipped, {ok} cached, {fail} failed"
            )

    print(f"\nDone. {ok} cached, {skip} already existed, {fail} failed.")
    if fail:
        print(
            f"Failed files will fall back to live pose_format loading at training time."
        )


if __name__ == "__main__":
    main()
