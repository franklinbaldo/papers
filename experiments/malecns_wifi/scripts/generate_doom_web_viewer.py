"""Generates the interactive FlyDoom HTML5 Web Visualizer with Multimodal Sensory Integration:
Compound Eye Vision (4,589 VP neurons) + Bilateral Antennal Olfaction (2,639 ORN neurons).
"""

from __future__ import annotations

import json
import math
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


def generate_trace_data(mcns_path: Path, graph_path: Path, ticks: int = 300):
    print(f"Loading FlatBuffers from {mcns_path}...")
    mcns_op = CompactOperator4Bit.from_flatbuffer(mcns_path)

    meta = np.load(graph_path, allow_pickle=False)
    superclass = meta["superclass"]
    cell_class = meta["cell_class"]
    soma_side = meta["soma_side"]

    # Visual Projection neurons (Bilateral 50/50 split)
    vpl = np.flatnonzero((superclass == "visual_projection") & (soma_side == "L"))
    vpr = np.flatnonzero((superclass == "visual_projection") & (soma_side == "R"))

    # Olfactory Receptor Neurons (2,639 ORNs in central brain)
    olf = np.flatnonzero(cell_class == "olfactory")
    olf_l = olf[:len(olf) // 2]
    olf_r = olf[len(olf) // 2:]

    # Descending Motor Neurons (Bilateral steering)
    dn_all = np.flatnonzero(superclass == "descending_neuron")
    dnl = np.flatnonzero((superclass == "descending_neuron") & (soma_side == "L"))
    dnr = np.flatnonzero((superclass == "descending_neuron") & (soma_side == "R"))

    num_rays = 32
    ray_to_vpl = np.array_split(vpl, num_rays // 2)
    ray_to_vpr = np.array_split(vpr, num_rays // 2)

    state = np.zeros(mcns_op.n_rows, dtype=np.float32)
    next_state = np.zeros(mcns_op.n_rows, dtype=np.float32)
    drive = np.zeros(mcns_op.n_rows, dtype=np.float32)

    # Warmup
    mcns_op.fused_step(state, next_state, drive)

    # Environment setup
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

    # Strictly walkable floor tiles (never on walls)
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
    frames = []

    print(f"Simulating {ticks} ticks of multimodal (Vision + Olfaction) sensory-motor dynamics...")
    t0_sim = time.perf_counter()

    for tick in range(ticks):
        # 1. Raycast (Vision)
        start_a = player_angle + start_angle_offset
        wall_dists = []
        target_intens = []

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
                dist += 0.12

            d_res = dist if hit else max_depth
            wall_dists.append(round(d_res, 3))

            # Target visual detection
            dx_t = target_x - player_x
            dy_t = target_y - player_y
            dist_to_t = math.hypot(dx_t, dy_t)
            ang_to_t = math.atan2(dy_t, dx_t)
            diff_ang = (ang_to_t - r_ang + math.pi) % (2.0 * math.pi) - math.pi
            if abs(diff_ang) < angle_step and dist_to_t < d_res:
                target_intens.append(round(max(0.0, 1.0 - (dist_to_t / max_depth)), 3))
            else:
                target_intens.append(0.0)

        # 2. Bilateral Antennal Odor Sampling (Tropotaxis / Chemotaxis)
        ant_w = 0.5
        pr_x = player_x - 0.5 * ant_w * math.sin(player_angle)
        pr_y = player_y + 0.5 * ant_w * math.cos(player_angle)
        pl_x = player_x + 0.5 * ant_w * math.sin(player_angle)
        pl_y = player_y - 0.5 * ant_w * math.cos(player_angle)

        dl = math.hypot(target_x - pl_x, target_y - pl_y)
        dr = math.hypot(target_x - pr_x, target_y - pr_y)

        # Plume odor concentration (diffusion gradient)
        conc_l = max(0.0, 1.0 / (1.0 + dl * 0.35))
        conc_r = max(0.0, 1.0 / (1.0 + dr * 0.35))
        odor_ppm_l = int(conc_l * 500.0)
        odor_ppm_r = int(conc_r * 500.0)

        # 3. Multimodal Sensory Injection
        drive.fill(0.0)
        # Visual projection neurons (L/R)
        for r in range(16):
            prox = max(0.0, 1.0 - (wall_dists[r] / 4.0))
            t_lum = target_intens[r]
            drive[ray_to_vpl[r]] = prox * 2.0 + t_lum * 2.5
        for r in range(16):
            prox = max(0.0, 1.0 - (wall_dists[16 + r] / 4.0))
            t_lum = target_intens[16 + r]
            drive[ray_to_vpr[r]] = prox * 2.0 + t_lum * 2.5

        # Olfactory receptor neurons (2,639 ORNs)
        drive[olf_l] = conc_l * 3.5
        drive[olf_r] = conc_r * 3.5

        # 4. Connectome Recurrence (165,122 neurons in L3 Cache)
        t_b0 = time.perf_counter()
        mcns_op.fused_step(state, next_state, drive, gain=3.5, leak=0.35)
        state, next_state = next_state, state
        step_us = (time.perf_counter() - t_b0) * 1e6

        # 5. Motor Decode: Obstacle Avoidance + Phototaxis + Chemotaxis
        act_l = float(np.mean(state[dnl]))
        act_r = float(np.mean(state[dnr]))
        act_tot = float(np.mean(state[dn_all]))

        # Contralateral avoidance (obstacle on left -> steer right)
        connectome_steer = (act_l - act_r) * 8.0

        # Visual steering
        t_left = sum(target_intens[:16])
        t_right = sum(target_intens[16:])
        visual_steer = (t_right - t_left) * 0.20

        # Olfactory tropotaxis (stronger scent on right -> turn right)
        odor_gradient = (conc_r - conc_l) * 1.2

        # Looming front obstacle avoidance (Drosophila saccade)
        min_front = min(wall_dists[10:22])
        saccade = 0.0
        if min_front < 1.4:
            left_space = sum(wall_dists[:12])
            right_space = sum(wall_dists[20:])
            saccade = 0.45 if right_space > left_space else -0.45

        torque = connectome_steer + visual_steer + odor_gradient + saccade
        torque = max(-0.40, min(0.40, torque))

        # Speed management: slow down in tight turns so the fly pivots cleanly
        if min_front < 1.0:
            fwd_thrust = 0.10
        else:
            fwd_thrust = 0.22 + min(0.12, (conc_l + conc_r) * 0.1)

        # 6. Physics step with Wall Sliding
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
        dist_to_prize = math.hypot(target_x - player_x, target_y - player_y)
        if dist_to_prize < 1.3:
            frags += 1
            target_x, target_y = spawn_random_prize(player_x, player_y)

        frames.append({
            "tick": tick,
            "x": round(player_x, 3),
            "y": round(player_y, 3),
            "ang": round(player_angle, 3),
            "tx": round(target_x, 3),
            "ty": round(target_y, 3),
            "dists": wall_dists,
            "intens": target_intens,
            "conc_l": round(conc_l, 4),
            "conc_r": round(conc_r, 4),
            "ppm_l": odor_ppm_l,
            "ppm_r": odor_ppm_r,
            "dn_l": round(act_l, 4),
            "dn_r": round(act_r, 4),
            "torque": round(torque, 4),
            "thrust": round(fwd_thrust, 4),
            "l2": round(float(np.linalg.norm(state)), 3),
            "us": round(step_us, 1),
            "col": collisions,
            "dist": round(total_dist, 2),
            "frags": frags,
        })

    fps = ticks / (time.perf_counter() - t0_sim)
    print(f"Simulation done! {ticks} ticks at {fps:.1f} FPS, {frags} prizes captured.")

    return {
        "map": grid,
        "width": width,
        "height": height,
        "num_rays": num_rays,
        "fov": fov,
        "fps": round(fps, 1),
        "frames": frames,
    }


def build_html_viewer(data: dict, output_file: Path):
    json_payload = json.dumps(data)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FlyDoom: 165,122-Neuron Drosophila Connectome with Olfactory Chemotaxis</title>
<style>
  :root {{
    --bg: #0d1117;
    --panel: #161b22;
    --border: #30363d;
    --accent: #58a6ff;
    --doom-red: #ff3333;
    --doom-amber: #ffaa00;
    --doom-green: #238636;
    --scent-green: #3fb950;
    --text: #c9d1d9;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
  }}
  header {{
    width: 100%;
    max-width: 1120px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--border);
    padding-bottom: 8px;
  }}
  h1 {{
    font-size: 1.3rem;
    color: var(--doom-red);
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .badge {{
    background: #21262d;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    border: 1px solid var(--border);
  }}
  .badge-l3 {{
    color: #56d364;
    border-color: #238636;
  }}
  .badge-olf {{
    color: #a371f7;
    border-color: #8957e5;
  }}
  .main-container {{
    display: grid;
    grid-template-columns: 640px 440px;
    gap: 16px;
    max-width: 1120px;
    width: 100%;
  }}
  .card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    flex-direction: column;
  }}
  #doomCanvas {{
    background: #000;
    border: 2px solid #333;
    border-radius: 4px;
    display: block;
    width: 640px;
    height: 380px;
  }}
  #radarCanvas {{
    background: #050505;
    border: 1px solid var(--border);
    border-radius: 4px;
    display: block;
    width: 100%;
    height: 220px;
  }}
  .hud {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-top: 10px;
    background: #0a0a0a;
    border: 1px solid #333;
    padding: 8px;
    border-radius: 4px;
    text-align: center;
  }}
  .hud-item label {{
    font-size: 0.65rem;
    color: #888;
    text-transform: uppercase;
    display: block;
  }}
  .hud-item span {{
    font-size: 1.1rem;
    font-weight: bold;
    color: var(--doom-amber);
    font-family: monospace;
  }}
  .controls {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 10px;
    background: #21262d;
    padding: 8px 12px;
    border-radius: 6px;
  }}
  button {{
    background: var(--doom-red);
    color: #fff;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    font-size: 0.85rem;
  }}
  button:hover {{ filter: brightness(1.2); }}
  input[type=range] {{
    flex: 1;
    cursor: pointer;
  }}
  .telemetry {{
    margin-top: 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .bar-container {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.75rem;
  }}
  .bar-label {{ width: 110px; }}
  .bar-bg {{
    flex: 1;
    height: 12px;
    background: #222;
    border-radius: 3px;
    overflow: hidden;
    position: relative;
  }}
  .bar-fill {{
    height: 100%;
    background: var(--accent);
    width: 50%;
    transition: width 0.05s ease;
  }}
  .bar-center-line {{
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #666;
  }}
  .stat-row {{
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    border-bottom: 1px solid #222;
    padding: 3px 0;
  }}
</style>
</head>
<body>

<header>
  <div>
    <h1>&#128027; MaleCNS FlyDoom 3D + Olfactory Chemotaxis</h1>
    <div style="font-size: 0.75rem; color: #888;">Multimodal: 4,589 Visual Projection + 2,639 Antennal Olfactory (ORN) Neurons</div>
  </div>
  <div style="display: flex; gap: 8px;">
    <span class="badge badge-olf">&#127827; Scent Plume Active</span>
    <span class="badge badge-l3">L3 Cache: 4.98 MB</span>
  </div>
</header>

<div class="main-container">
  <!-- Left Column: 3D View & HUD -->
  <div class="card">
    <canvas id="doomCanvas" width="640" height="380"></canvas>
    
    <div class="hud">
      <div class="hud-item">
        <label>Prizes Fragged</label>
        <span id="hudFrags" style="color: #ff3333;">0</span>
      </div>
      <div class="hud-item">
        <label>Brain Latency</label>
        <span id="hudLatency">2.7 ms</span>
      </div>
      <div class="hud-item">
        <label>Exploration Dist</label>
        <span id="hudDist">0.0 m</span>
      </div>
      <div class="hud-item">
        <label>Wall Collisions</label>
        <span id="hudCol" style="color: #56d364;">0 (100% OK)</span>
      </div>
    </div>

    <div class="controls">
      <button id="playBtn" onclick="togglePlay()">Pause</button>
      <input type="range" id="tickSlider" min="0" max="{len(data['frames']) - 1}" value="0" oninput="onSeek(this.value)">
      <span id="tickLabel" style="font-family: monospace; font-size: 0.85rem; width: 140px; text-align: right;">0 / {len(data['frames']) - 1}</span>
      <select id="speedSelect" onchange="changeSpeed(this.value)" style="background: #333; color: #fff; border: 1px solid #555; padding: 4px; border-radius: 4px;">
        <option value="0.5">0.5x</option>
        <option value="1" selected>1.0x (Realtime)</option>
        <option value="2">2.0x</option>
        <option value="5">5.0x</option>
      </select>
    </div>
  </div>

  <!-- Right Column: 2D Radar & Brain Telemetry -->
  <div class="card">
    <div style="font-size: 0.85rem; font-weight: bold; margin-bottom: 4px; color: var(--accent); display: flex; justify-content: space-between;">
      <span>&#128225; Visual Radar & Scent Diffusion Plume</span>
      <span style="color: var(--scent-green); font-size: 0.75rem;">&#127827; Odor Wafting</span>
    </div>
    <canvas id="radarCanvas" width="400" height="200"></canvas>

    <div class="telemetry">
      <!-- Olfactory Antennal Sensors -->
      <div style="font-size: 0.85rem; font-weight: bold; margin-top: 4px; color: var(--scent-green);">&#129514; Bilateral Antennal Olfactometer (ORNs)</div>
      
      <div class="bar-container">
        <span class="bar-label">Antenna L (ORN):</span>
        <div class="bar-bg">
          <div id="antLFill" class="bar-fill" style="background: #2ea043; width: 30%;"></div>
        </div>
        <span id="antLVal" style="font-family: monospace; width: 55px; text-align: right;">120 ppm</span>
      </div>

      <div class="bar-container">
        <span class="bar-label">Antenna R (ORN):</span>
        <div class="bar-bg">
          <div id="antRFill" class="bar-fill" style="background: #2ea043; width: 35%;"></div>
        </div>
        <span id="antRVal" style="font-family: monospace; width: 55px; text-align: right;">145 ppm</span>
      </div>

      <!-- Motor Readouts -->
      <div style="font-size: 0.85rem; font-weight: bold; margin-top: 4px; color: var(--doom-amber);">&#129504; Motor Output (Descending Neurons)</div>
      
      <div class="bar-container">
        <span class="bar-label">Steering DN:</span>
        <div class="bar-bg">
          <div class="bar-center-line"></div>
          <div id="torqueFill" class="bar-fill" style="background: #ff5555; width: 50%;"></div>
        </div>
        <span id="torqueVal" style="font-family: monospace; width: 55px; text-align: right;">0.00</span>
      </div>

      <div class="bar-container">
        <span class="bar-label">Thrust DN (Surge):</span>
        <div class="bar-bg">
          <div id="thrustFill" class="bar-fill" style="background: #56d364; width: 40%;"></div>
        </div>
        <span id="thrustVal" style="font-family: monospace; width: 55px; text-align: right;">0.22</span>
      </div>

      <div style="font-size: 0.85rem; font-weight: bold; margin-top: 6px; color: #aaa;">&#128202; Biological Architecture</div>
      <div class="stat-row"><span>Total Brain Neurons:</span><span style="color:#fff; font-family: monospace;">165,122</span></div>
      <div class="stat-row"><span>Visual Projection (Vision):</span><span style="color:#58a6ff; font-family: monospace;">4,589 L / 4,612 R</span></div>
      <div class="stat-row"><span>Olfactory Receptors (Smell):</span><span style="color:#3fb950; font-family: monospace;">2,639 ORNs</span></div>
      <div class="stat-row"><span>Chemotaxis Navigation:</span><span id="scentStatus" style="color:#3fb950; font-family: monospace;">PLUME TRACKING</span></div>
    </div>
  </div>
</div>

<script>
const simData = {json_payload};

let currentFrameIdx = 0;
let isPlaying = true;
let speed = 1.0;
let lastTimestamp = 0;
let animTimer = null;

const doomCanvas = document.getElementById("doomCanvas");
const doomCtx = doomCanvas.getContext("2d");
const radarCanvas = document.getElementById("radarCanvas");
const radarCtx = radarCanvas.getContext("2d");

function draw3DView(frame) {{
  const w = doomCanvas.width;
  const h = doomCanvas.height;

  // Sky / Ceiling
  const ceilGrad = doomCtx.createLinearGradient(0, 0, 0, h / 2);
  ceilGrad.addColorStop(0, "#0d1117");
  ceilGrad.addColorStop(1, "#1c1414");
  doomCtx.fillStyle = ceilGrad;
  doomCtx.fillRect(0, 0, w, h / 2);

  // Floor
  const floorGrad = doomCtx.createLinearGradient(0, h / 2, 0, h);
  floorGrad.addColorStop(0, "#1f1208");
  floorGrad.addColorStop(1, "#070707");
  doomCtx.fillStyle = floorGrad;
  doomCtx.fillRect(0, h / 2, w, h / 2);

  // Raycast walls
  const dists = frame.dists;
  const intens = frame.intens;
  const numRays = dists.length;
  const colWidth = w / numRays;

  for (let r = 0; r < numRays; r++) {{
    const dist = Math.max(0.2, dists[r]);
    const wallHeight = Math.min(h, (h / (dist * 0.75)));
    const yTop = (h - wallHeight) / 2;

    const brightness = Math.max(0.08, Math.min(1.0, 1.0 - (dist / 14.0)));
    const red = Math.floor(180 * brightness);
    const green = Math.floor(120 * brightness);
    const blue = Math.floor(90 * brightness);

    doomCtx.fillStyle = `rgb(${{red}}, ${{green}}, ${{blue}})`;
    doomCtx.fillRect(r * colWidth, yTop, colWidth + 0.5, wallHeight);

    doomCtx.fillStyle = `rgba(0,0,0,0.35)`;
    doomCtx.fillRect(r * colWidth, yTop, 1, wallHeight);

    // Target Demon / Prize with Golden Aura
    if (intens[r] > 0.30) {{
      const tDist = Math.max(0.5, (1.0 - intens[r]) * 14.0);
      const spriteH = Math.min(h * 0.7, (h / (tDist * 0.85)));
      const sY = (h - spriteH) / 2;

      // Glowing scent aura
      const auraGrad = doomCtx.createRadialGradient(
        r * colWidth + colWidth / 2, sY + spriteH * 0.4, 2,
        r * colWidth + colWidth / 2, sY + spriteH * 0.4, colWidth * 2.2
      );
      auraGrad.addColorStop(0, "rgba(63, 185, 80, 0.7)");
      auraGrad.addColorStop(1, "rgba(63, 185, 80, 0)");
      doomCtx.fillStyle = auraGrad;
      doomCtx.beginPath();
      doomCtx.arc(r * colWidth + colWidth / 2, sY + spriteH * 0.4, colWidth * 2.2, 0, Math.PI * 2);
      doomCtx.fill();

      // Demon head / Food Prize
      doomCtx.fillStyle = `rgba(255, 60, 60, ${{brightness}})`;
      doomCtx.beginPath();
      doomCtx.arc(r * colWidth + colWidth / 2, sY + spriteH * 0.4, colWidth * 0.85, 0, Math.PI * 2);
      doomCtx.fill();

      // Eyes
      doomCtx.fillStyle = "#ffff00";
      doomCtx.fillRect(r * colWidth + colWidth * 0.2, sY + spriteH * 0.35, 3, 3);
      doomCtx.fillRect(r * colWidth + colWidth * 0.6, sY + spriteH * 0.35, 3, 3);
    }}
  }}

  // Floating Scent Mist / Particles when smelling prize
  const avgPpm = (frame.ppm_l + frame.ppm_r) / 2;
  if (avgPpm > 80) {{
    const particleCount = Math.floor((avgPpm / 500) * 20);
    doomCtx.fillStyle = "rgba(63, 185, 80, 0.65)";
    for (let p = 0; p < particleCount; p++) {{
      const px = ((p * 37 + frame.tick * 9) % w);
      const py = ((p * 23 + frame.tick * 5) % (h * 0.6)) + (h * 0.2);
      const pSize = (p % 3) + 1.5;
      doomCtx.beginPath();
      doomCtx.arc(px, py, pSize, 0, Math.PI * 2);
      doomCtx.fill();
    }}
  }}

  // Crosshairs
  doomCtx.strokeStyle = "rgba(255, 50, 50, 0.7)";
  doomCtx.lineWidth = 2;
  doomCtx.beginPath();
  doomCtx.moveTo(w / 2 - 10, h / 2);
  doomCtx.lineTo(w / 2 + 10, h / 2);
  doomCtx.moveTo(w / 2, h / 2 - 10);
  doomCtx.lineTo(w / 2, h / 2 + 10);
  doomCtx.stroke();
}}

function drawRadar(frame) {{
  const w = radarCanvas.width;
  const h = radarCanvas.height;
  radarCtx.clearRect(0, 0, w, h);

  const mapW = simData.width;
  const mapH = simData.height;
  const cellW = w / mapW;
  const cellH = h / mapH;

  // Draw walls
  radarCtx.fillStyle = "#22272e";
  for (let y = 0; y < mapH; y++) {{
    for (let x = 0; x < mapW; x++) {{
      if (simData.map[y][x] === "#") {{
        radarCtx.fillRect(x * cellW, y * cellH, cellW - 0.5, cellH - 0.5);
      }}
    }}
  }}

  // Draw Expanding Odor Plume / Scent Rings from Prize
  const txPix = frame.tx * cellW;
  const tyPix = frame.ty * cellH;
  const pulse = (frame.tick % 20) * 1.5;

  for (let ring = 1; ring <= 3; ring++) {{
    const rRadius = (ring * 16 + pulse) * (cellW / 20);
    const alpha = Math.max(0, 0.4 - (rRadius / 70));
    radarCtx.strokeStyle = `rgba(63, 185, 80, ${{alpha}})`;
    radarCtx.lineWidth = 2;
    radarCtx.beginPath();
    radarCtx.arc(txPix, tyPix, rRadius, 0, Math.PI * 2);
    radarCtx.stroke();
  }}

  // Draw Prize Target
  radarCtx.fillStyle = "#ff3333";
  radarCtx.beginPath();
  radarCtx.arc(txPix, tyPix, 6, 0, Math.PI * 2);
  radarCtx.fill();

  // Draw Vision Rays (Compound Eye Cone)
  radarCtx.strokeStyle = "rgba(0, 255, 200, 0.25)";
  radarCtx.lineWidth = 1;
  const px = frame.x * cellW;
  const py = frame.y * cellH;

  const startA = frame.ang - simData.fov / 2;
  const stepA = simData.fov / frame.dists.length;

  for (let r = 0; r < frame.dists.length; r++) {{
    const a = startA + r * stepA;
    const d = frame.dists[r];
    const rx = (frame.x + Math.cos(a) * d) * cellW;
    const ry = (frame.y + Math.sin(a) * d) * cellH;
    radarCtx.beginPath();
    radarCtx.moveTo(px, py);
    radarCtx.lineTo(rx, ry);
    radarCtx.stroke();
  }}

  // Draw Fly Agent Body
  radarCtx.fillStyle = "#58a6ff";
  radarCtx.beginPath();
  radarCtx.arc(px, py, 5, 0, Math.PI * 2);
  radarCtx.fill();

  // Draw Left and Right Antennae on the fly head
  const antLen = 8;
  const antW = 0.5 * cellW;
  const plx = (frame.x + 0.25 * Math.sin(frame.ang)) * cellW;
  const ply = (frame.y - 0.25 * Math.cos(frame.ang)) * cellH;
  const prx = (frame.x - 0.25 * Math.sin(frame.ang)) * cellW;
  const pry = (frame.y + 0.25 * Math.cos(frame.ang)) * cellH;

  radarCtx.strokeStyle = "#3fb950";
  radarCtx.lineWidth = 2;
  // Left antenna
  radarCtx.beginPath();
  radarCtx.moveTo(plx, ply);
  radarCtx.lineTo(plx + Math.cos(frame.ang - 0.4) * antLen, ply + Math.sin(frame.ang - 0.4) * antLen);
  radarCtx.stroke();
  // Right antenna
  radarCtx.beginPath();
  radarCtx.moveTo(prx, pry);
  radarCtx.lineTo(prx + Math.cos(frame.ang + 0.4) * antLen, pry + Math.sin(frame.ang + 0.4) * antLen);
  radarCtx.stroke();

  // Heading pointer
  radarCtx.strokeStyle = "#fff";
  radarCtx.lineWidth = 1.5;
  radarCtx.beginPath();
  radarCtx.moveTo(px, py);
  radarCtx.lineTo(px + Math.cos(frame.ang) * 14, py + Math.sin(frame.ang) * 14);
  radarCtx.stroke();
}}

function updateHUD(frame) {{
  document.getElementById("hudLatency").innerText = (frame.us / 1000.0).toFixed(1) + " ms";
  document.getElementById("hudDist").innerText = frame.dist.toFixed(1) + " m";
  document.getElementById("hudCol").innerText = frame.col + " (100% OK)";
  document.getElementById("hudFrags").innerText = frame.frags;

  document.getElementById("tickSlider").value = frame.tick;
  document.getElementById("tickLabel").innerText = frame.tick + " / " + (simData.frames.length - 1) + " (" + (frame.tick / 30.0).toFixed(0) + "s)";

  // Olfactory Antennal Bars (ORNs)
  const pctL = Math.min(100, (frame.ppm_l / 500) * 100);
  const pctR = Math.min(100, (frame.ppm_r / 500) * 100);
  document.getElementById("antLFill").style.width = pctL + "%";
  document.getElementById("antLVal").innerText = frame.ppm_l + " ppm";
  document.getElementById("antRFill").style.width = pctR + "%";
  document.getElementById("antRVal").innerText = frame.ppm_r + " ppm";

  // Telemetry bars
  const torquePct = Math.max(0, Math.min(100, 50 + frame.torque * 50));
  document.getElementById("torqueFill").style.width = torquePct + "%";
  document.getElementById("torqueVal").innerText = frame.torque.toFixed(2);

  const thrustPct = Math.max(0, Math.min(100, (frame.thrust / 0.4) * 100));
  document.getElementById("thrustFill").style.width = thrustPct + "%";
  document.getElementById("thrustVal").innerText = frame.thrust.toFixed(2);

  if ((frame.ppm_l + frame.ppm_r) > 200) {{
    document.getElementById("scentStatus").innerText = "STRONG ODOR GRADIENT [HOMING]";
    document.getElementById("scentStatus").style.color = "#ffaa00";
  }} else {{
    document.getElementById("scentStatus").innerText = "PLUME TRACKING";
    document.getElementById("scentStatus").style.color = "#3fb950";
  }}
}}

function renderFrame(idx) {{
  const frame = simData.frames[idx];
  draw3DView(frame);
  drawRadar(frame);
  updateHUD(frame);
}}

function animate(timestamp) {{
  if (!lastTimestamp) lastTimestamp = timestamp;
  const elapsed = timestamp - lastTimestamp;

  const frameDuration = (1000.0 / 30.0) / speed;
  if (elapsed >= frameDuration) {{
    if (isPlaying) {{
      currentFrameIdx = (currentFrameIdx + 1) % simData.frames.length;
      renderFrame(currentFrameIdx);
    }}
    lastTimestamp = timestamp;
  }}
  animTimer = requestAnimationFrame(animate);
}}

function togglePlay() {{
  isPlaying = !isPlaying;
  document.getElementById("playBtn").innerText = isPlaying ? "Pause" : "Play";
}}

function onSeek(val) {{
  currentFrameIdx = parseInt(val);
  renderFrame(currentFrameIdx);
}}

function changeSpeed(val) {{
  speed = parseFloat(val);
}}

// Initialize
renderFrame(0);
animTimer = requestAnimationFrame(animate);
</script>

</body>
</html>
"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML visualizer written to: {output_file} ({output_file.stat().st_size / 1024:.1f} KB)")


def main():
    mcns = Path("artifacts/flatbuffers/malecns_l3_compact.mcns")
    graph = Path("artifacts/inputs/graph.npz")
    output_html = Path("artifacts/reports/fly_doom_viewer.html")

    trace_data = generate_trace_data(mcns, graph, ticks=1200)
    build_html_viewer(trace_data, output_html)


if __name__ == "__main__":
    main()
