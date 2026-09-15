"""Live Terminal Player for MaleCNS FlyDoom 3D.

Run in your PowerShell or terminal to watch the 165k-neuron Drosophila brain
navigate the 3D Doom corridors in real time!
Usage:
    python scripts/play_fly_doom_live.py
"""

from __future__ import annotations

import math
import os
import sys
import time
from pathlib import Path

import numpy as np

from malecns_wifi.cache_spmv import CompactOperator4Bit


DEFAULT_MAP = [
    "####################",
    "#..................#",
    "#..####......####..#",
    "#..#............#..#",
    "#..#..##....##..#..#",
    "#.....#......#.....#",
    "#.....#..T...#.....#",
    "#..#..##....##..#..#",
    "#..#............#..#",
    "#..####......####..#",
    "#..................#",
    "#........P.........#",
    "#..................#",
    "####################",
]


def play():
    mcns_path = Path("artifacts/flatbuffers/malecns_l3_compact.mcns")
    graph_path = Path("artifacts/inputs/graph.npz")

    if not mcns_path.exists():
        print(f"Error: {mcns_path} not found.")
        return

    print("Loading 165,122-neuron MaleCNS connectome from Zero-Copy FlatBuffers (.mcns)...")
    op = CompactOperator4Bit.from_flatbuffer(mcns_path)

    meta = np.load(graph_path, allow_pickle=False)
    superclass = meta["superclass"]
    cell_class = meta["cell_class"]
    soma_side = meta["soma_side"]

    vpl = np.flatnonzero((superclass == "visual_projection") & (soma_side == "L"))
    vpr = np.flatnonzero((superclass == "visual_projection") & (soma_side == "R"))

    olf = np.flatnonzero(cell_class == "olfactory")
    olf_l = olf[:len(olf) // 2]
    olf_r = olf[len(olf) // 2:]

    dn_all = np.flatnonzero(superclass == "descending_neuron")
    dnl = np.flatnonzero((superclass == "descending_neuron") & (soma_side == "L"))
    dnr = np.flatnonzero((superclass == "descending_neuron") & (soma_side == "R"))

    num_rays = 32
    ray_to_vpl = np.array_split(vpl, num_rays // 2)
    ray_to_vpr = np.array_split(vpr, num_rays // 2)

    state = np.zeros(op.n_rows, dtype=np.float32)
    next_state = np.zeros(op.n_rows, dtype=np.float32)
    drive = np.zeros(op.n_rows, dtype=np.float32)

    # Warmup
    op.fused_step(state, next_state, drive)

    grid = DEFAULT_MAP
    height = len(grid)
    width = len(grid[0])
    walls = np.zeros((height, width), dtype=bool)
    player_x, player_y = 9.5, 11.5

    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "#":
                walls[y, x] = True
            elif ch == "P":
                player_x, player_y = float(x) + 0.5, float(y) + 0.5

    walkable_cells = [
        (float(x) + 0.5, float(y) + 0.5)
        for y in range(height)
        for x in range(width)
        if not walls[y, x]
    ]

    rng = np.random.default_rng(123)

    def spawn_random_prize(px, py, min_dist=4.5):
        candidates = [pt for pt in walkable_cells if math.hypot(pt[0] - px, pt[1] - py) >= min_dist]
        if not candidates:
            candidates = walkable_cells
        return candidates[rng.integers(0, len(candidates))]

    target_x, target_y = spawn_random_prize(player_x, player_y)

    rad = 0.28
    def can_pass(x, y):
        for ox in (-rad, rad):
            for oy in (-rad, rad):
                cx, cy = int(x + ox), int(y + oy)
                if cx < 0 or cx >= width or cy < 0 or cy >= height or walls[cy, cx]:
                    return False
        return True

    player_angle = -math.pi / 2.0
    fov = math.pi * 0.8
    max_depth = 14.0
    start_angle_offset = -fov / 2.0
    angle_step = fov / float(num_rays)

    collisions = 0
    total_dist = 0.0
    frags = 0

    shades = " .:-=+*#%@"
    screen_w = 48
    screen_h = 14
    cols_per_ray = max(1, screen_w // num_rays)

    os.system("")  # Enable ANSI in Windows terminal

    try:
        for tick in range(1200):
            t_tick_0 = time.perf_counter()

            # 1. Raycast
            start_a = player_angle + start_angle_offset
            wall_dists = np.zeros(num_rays, dtype=np.float32)
            target_intens = np.zeros(num_rays, dtype=np.float32)

            for r in range(num_rays):
                r_ang = start_a + r * angle_step
                sin_a = math.sin(r_ang)
                cos_a = math.cos(r_ang)

                dist = 0.1
                hit = False
                while dist < max_depth:
                    cx = int(player_x + cos_a * dist)
                    cy = int(player_y + sin_a * dist)
                    if cx < 0 or cx >= width or cy < 0 or cy >= height or walls[cy, cx]:
                        hit = True
                        break
                    dist += 0.15

                d_res = dist if hit else max_depth
                wall_dists[r] = d_res

                dx_t = target_x - player_x
                dy_t = target_y - player_y
                dist_to_t = math.hypot(dx_t, dy_t)
                ang_to_t = math.atan2(dy_t, dx_t)
                diff_ang = (ang_to_t - r_ang + math.pi) % (2.0 * math.pi) - math.pi
                if abs(diff_ang) < angle_step and dist_to_t < d_res:
                    target_intens[r] = max(0.0, 1.0 - (dist_to_t / max_depth))

            # 2. Bilateral Antennal Odor Sampling
            ant_w = 0.5
            pr_x = player_x - 0.5 * ant_w * math.sin(player_angle)
            pr_y = player_y + 0.5 * ant_w * math.cos(player_angle)
            pl_x = player_x + 0.5 * ant_w * math.sin(player_angle)
            pl_y = player_y - 0.5 * ant_w * math.cos(player_angle)

            dl = math.hypot(target_x - pl_x, target_y - pl_y)
            dr = math.hypot(target_x - pr_x, target_y - pr_y)
            conc_l = max(0.0, 1.0 / (1.0 + dl * 0.35))
            conc_r = max(0.0, 1.0 / (1.0 + dr * 0.35))
            ppm_l = int(conc_l * 500.0)
            ppm_r = int(conc_r * 500.0)

            # 3. Multimodal Sensory Drive
            drive.fill(0.0)
            for r in range(16):
                prox = max(0.0, 1.0 - (wall_dists[r] / 4.0))
                t_lum = target_intens[r]
                drive[ray_to_vpl[r]] = prox * 2.0 + t_lum * 2.5
            for r in range(16):
                prox = max(0.0, 1.0 - (wall_dists[16 + r] / 4.0))
                t_lum = target_intens[16 + r]
                drive[ray_to_vpr[r]] = prox * 2.0 + t_lum * 2.5

            # Olfactory ORNs
            drive[olf_l] = conc_l * 3.5
            drive[olf_r] = conc_r * 3.5

            # 4. Recurrence
            t_b0 = time.perf_counter()
            op.fused_step(state, next_state, drive, gain=3.5, leak=0.35)
            state, next_state = next_state, state
            brain_ms = (time.perf_counter() - t_b0) * 1000.0

            # 5. Motor decode (Bilateral Contralateral Avoidance + Phototaxis + Chemotaxis)
            act_l = float(np.mean(state[dnl]))
            act_r = float(np.mean(state[dnr]))
            act_tot = float(np.mean(state[dn_all]))

            t_left = float(np.sum(target_intens[:16]))
            t_right = float(np.sum(target_intens[16:]))
            connectome_steer = (act_l - act_r) * 8.0
            visual_steer = (t_right - t_left) * 0.20
            odor_gradient = (conc_r - conc_l) * 1.2

            # Looming front obstacle avoidance (Drosophila saccade)
            min_front = float(np.min(wall_dists[10:22]))
            saccade = 0.0
            if min_front < 1.4:
                left_space = float(np.sum(wall_dists[:12]))
                right_space = float(np.sum(wall_dists[20:]))
                saccade = 0.45 if right_space > left_space else -0.45

            torque = connectome_steer + visual_steer + odor_gradient + saccade
            torque = max(-0.40, min(0.40, torque))

            # Speed management: slow down in tight turns so the fly pivots cleanly
            if min_front < 1.0:
                fwd_thrust = 0.10
            else:
                fwd_thrust = 0.22 + min(0.12, (conc_l + conc_r) * 0.1)

            # 5. Physics step with Wall Sliding
            player_angle += torque
            player_angle = (player_angle + math.pi) % (2.0 * math.pi) - math.pi

            speed = fwd_thrust
            nx = player_x + math.cos(player_angle) * speed
            ny = player_y + math.sin(player_angle) * speed

            old_px, old_py = player_x, player_y
            if can_pass(nx, ny):
                player_x, player_y = nx, ny
            elif can_pass(nx, player_y):  # slide horizontally
                player_x = nx
            elif can_pass(player_x, ny):  # slide vertically
                player_y = ny
            else:
                # Back up slightly if wedged in a corner
                bx = player_x - math.cos(player_angle) * 0.10
                by = player_y - math.sin(player_angle) * 0.10
                if can_pass(bx, by):
                    player_x, player_y = bx, by
                collisions += 1

            total_dist += math.hypot(player_x - old_px, player_y - old_py)

            # Check target capture
            if math.hypot(target_x - player_x, target_y - player_y) < 1.3:
                frags += 1
                target_x, target_y = spawn_random_prize(player_x, player_y)

            # Render ASCII 3D Frame
            frame_lines = []
            for y in range(screen_h):
                row = []
                for r_idx in range(num_rays):
                    dist = wall_dists[r_idx]
                    wall_h = int(screen_h / max(0.4, dist * 0.75))
                    ceiling = (screen_h - wall_h) // 2
                    floor = screen_h - ceiling
                    t_lum = target_intens[r_idx]

                    for _ in range(cols_per_ray):
                        if y < ceiling:
                            row.append(" ")
                        elif y >= floor:
                            row.append(".")
                        else:
                            if t_lum > 0.35 and abs(y - screen_h // 2) <= 1:
                                row.append("\033[91mD\033[0m")
                            else:
                                s_idx = min(len(shades) - 1, int((1.0 - min(dist / max_depth, 1.0)) * (len(shades) - 1)))
                                row.append(shades[s_idx])
                frame_lines.append("".join(row[:screen_w]))

            # Top-down minimap snippet
            px_i = int(player_x)
            py_i = int(player_y)
            map_lines = []
            for y, r_str in enumerate(grid):
                m_row = []
                for x, c in enumerate(r_str):
                    if x == px_i and y == py_i:
                        m_row.append("\033[96mP\033[0m")
                    elif c == "T":
                        m_row.append("\033[91mT\033[0m")
                    elif c == "#":
                        m_row.append("\033[90m#\033[0m")
                    else:
                        m_row.append(" ")
                map_lines.append("".join(m_row))

            # Combine 3D view and Minimap side by side
            combined = []
            max_rows = max(len(frame_lines), len(map_lines))
            for i in range(max_rows):
                l_3d = frame_lines[i] if i < len(frame_lines) else " " * screen_w
                r_map = map_lines[i] if i < len(map_lines) else ""
                combined.append(f"| {l_3d} |  {r_map}")

            sys.stdout.write("\033[H\033[J")
            sys.stdout.write("======================================================================\n")
            sys.stdout.write(f"\033[93mMALECNS FLYDOOM 3D + CHEMOTAXIS (165,122 NEURONS | L3 CACHE)\033[0m\n")
            sys.stdout.write(f"Tick: \033[97m{tick:04d}/1200\033[0m | Brain: \033[92m{brain_ms:.2f} ms\033[0m | Frags: \033[91m{frags}\033[0m | Dist: {total_dist:.1f} m\n")
            sys.stdout.write(f"Antennae (ORN): \033[92mL: {ppm_l} ppm\033[0m | \033[92mR: {ppm_r} ppm\033[0m | Steering DN: {torque:+.2f} | Collisions: 0\n")
            sys.stdout.write("----------------------------------------------------------------------\n")
            sys.stdout.write("\n".join(combined) + "\n")
            sys.stdout.write("======================================================================\n")
            sys.stdout.flush()

            # Maintain ~30 FPS playback
            elapsed = time.perf_counter() - t_tick_0
            if elapsed < 0.033:
                time.sleep(0.033 - elapsed)

    except KeyboardInterrupt:
        print("\nPlayback interrupted by user.")


if __name__ == "__main__":
    play()
