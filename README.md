# Deterministic Wave Engine (DWE) - Version 5.0
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Built with Rust](https://img.shields.io/badge/Built%20with-Rust-orange.svg)](https://www.rust-lang.org/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.20417434-blue.svg)](https://doi.org/10.5281/zenodo.20417434)

## A Mathematical Experiment in Classical Hydrodynamics & Quantum Analogs

The **Deterministic Wave Engine (DWE)** is an ongoing mathematical experiment and high-performance computational platform written in Rust, powered by WGSL Compute Shaders (WebGPU). Its primary goal is to explain quantum mechanical phenomena strictly from the foundational premises of **traditional, classical physics**.

In this framework, what modern quantum mechanics refers to as "quantum fields" is explicitly modeled as the hydrodynamic, acoustic, and thermodynamic behavior of the vacuum. The DWE treats this vacuum not as an empty void, but as a physical **viscoelastic fluid** possessing structural spatial tension ($\gamma_0$).

The most accurate physical parallel to this software experiment is the study of **Hydrodynamic Quantum Analogs (HQAs)**. By framing the universe's substrate as a fluid, this engine demonstrates *in silico* that quantum statistical distributions (Born's Law) can emerge entirely from **deterministic, local-realist space-time trajectories**.

---

## 🎯 Core Simulation 1: The Pfleegor-Mandel Experiment (1967)

Unlike traditional models that simulate the standard Double-Slit experiment, **this engine does not use physical slits**. Instead, it simulates the groundbreaking **Pfleegor-Mandel Experiment of 1967**.

In 1967, physicists R. L. Pfleegor and Leonard Mandel achieved what was previously thought impossible: generating quantum interference using two completely independent sources of light.

**The Setup Simulated in DWE:**

* **Two Independent Lasers:** Laser A (left) and Laser B (right) are turned on and angled to converge at the exact same point on a detector screen.
* **Extreme Attenuation:** The intensity of the lasers is reduced to such an extreme level that **only one photon exists inside the apparatus at any given time**. A photon is emitted, strikes the screen, and only then is another photon born.
* **No Synchronization:** There is absolutely no physical or electrical connection synchronizing the internal emission of the lasers. They are two separate machines.

Under orthodox quantum mechanics, interference occurs because a photon exists in a superposition and "interferes with itself" by passing through two slits simultaneously. However, in the Pfleegor-Mandel setup, the photon clearly originates from either Laser A *or* Laser B.

**The DWE Fluidic Solution:** The engine resolves this paradox deterministically. While the photon is a discrete particle, its movement through the viscoelastic vacuum generates an acoustic shockwave (a Pilot Wave). The vacuum retains an *acoustic memory* of these waves. Therefore, a photon emitted by Laser A interacts with the residual pressure ripples left in the vacuum by a previous photon from Laser B, guiding the new particle into discrete interference fringes without requiring quantum superposition.

---

## 🌀 Core Simulation 2: The Hong-Ou-Mandel (HOM) Effect (1987)

While the Pfleegor-Mandel setup challenges spatial superposition, the **Hong-Ou-Mandel (HOM) effect** is the ultimate test of quantum entanglement and bosonic indistinguishability.

**The Setup Simulated in DWE:**

* **The 50/50 Beam Splitter:** Modeled via a Symmetric Dielectric Grating, where two particles converge simultaneously from orthogonal directions.
* **The Quantum Expectation:** When two identical photons enter opposite ports simultaneously, they "bunch" together and exit the same port, completely canceling out the probability of exiting separately (the HOM Dip).

**The DWE Fluidic Solution:** The engine reproduces this purely through deterministic fluid mechanics. Photons are modeled as counter-rotating fluidic vortices (Topological Solitons). As they perfectly synchronize at the beam splitter's core, their mutual induction (Quantum Magnus Effect) draws them together, while their thermo-acoustic wakes interfere, creating a high-pressure repulsive shockwave. This inelastic geometric block prevents independent Maxwell-Boltzmann scattering. The spatial momentum forces both vortices to drag each other into the same free-flowing output channel, modeling the $|2,0\rangle$ or $|0,2\rangle$ bosonic states through Newtonian restrictions.

**The 4-State Topological Matrix:**
By altering initial hidden variables (sub-pixel spatial phases, $\Delta = 0.0314$) and temporal coherence, the DWE maps the four scattering possibilities:
1. **Synchronous (Phase A):** Perfect bunching (Bottom-Left output).
2. **Synchronous (Phase B - Half-Wave Shift):** Perfect bunching (Top-Right output).
3. **Asynchronous (Temporal Delay 1):** Classical transmission (Broken HOM symmetry).
4. **Asynchronous (Temporal Delay 2):** Classical reflection (Broken HOM symmetry).

![Topological Scattering Matrix](matriz_4_possibilidades.png)

---

## 🔬 Computational Physics Framework (V5.0)

Standard quantum mechanics relies on abstract probability waves ($\Psi$). The DWE replaces this abstraction with strict micro-fluid mechanics:

1. **The Double-Cone (Spindle) Vortex (Invariant Spin):** Photons are modeled as physical topological defects—two cones joined at their circular base. The photon's momentum is forward, while its equator possesses an intrinsic, invariant angular momentum (Spin/Helicity, $\pm\omega$).
2. **Conical Laser Emission (Box-Muller Transformation):** Real-world lasers do not emit rectangular blocks of light. DWE implements a true point-source conical beam using the *Box-Muller Transform*, delivering a perfect Gaussian intensity envelope.
3. **Vacuum Memory & Acoustic Friction:** As the rotating vortex-photons travel through the vacuum, they leave thermodynamic energy ripples. Subsequent particles interact with this active fluidic gradient, steering them deterministically into macroscopic patterns.
4. **Topological Compression & Emergent Frequency:** Higher-energy particles are ultra-compacted, rigid vortex cores. As this bubble travels, it creates a rhythmic trailing wave-train of pressure ripples. The **frequency ($\nu$)** is simply the spatial periodicity of this acoustic shockwave wake.

---

## 📊 Experimental Matrix (The Four Quadrants)

![pfleegor_mandel_raw_data_full10k](analytics/pfleegor_mandel_raw_data_full10k.png)

The main simulation (`fenda_shader.wgsl`) executes four distinct operational states, toggling hydrodynamic parameters (turbulence, fluid memory, and spin) sent from the Rust host to the GPU kernel:

| Quadrant / Dataset | Setup | Physical Interpretation (Parameters) | Emergent Visual Pattern |
| --- | --- | --- | --- |
| **A: Two Lasers** | 2 Lasers | **Classical Dispersion / No Memory:** Inert particles in a sterile vacuum. Acoustic memory and spin are disabled. | Purely ballistic/Gaussian smooth dispersion envelope overlapping at the center. |
| **B: Fluid Reality** | 2 Lasers | **Turbulence + Memory:** Active vacuum reacting to acoustic pilot waves. | Rudimentary diffraction peaks begin to emerge due to the fluid path memory steering the particles. |
| **C: Quantum Magnus Effect** | 2 Lasers | **Memory + Spin + Turbulence:** Full DWE model. Deterministic spin-friction coupled with the vacuum's structural tension gradient. | Hyper-sharp, defined interference grid (Fraunhofer lines) emerging from completely independent sources. |
| **D: Stern-Gerlach** | **ONLY 1 LASER** | **Spin + Transverse Magnetic Field:** Employs a simulated magnetic field gradient to attract/deflect photons based on their intrinsic spin (clockwise vs. counter-clockwise). | Macro-separation of the single beam into two distinct peaks, demonstrating spatial splitting driven purely by rotational helicity. |

---

## 📈 Statistical Buildup and the Emergence of $|\Psi|^2$

A critical distinction of this experiment is its strict adherence to individual particle trajectory simulation. The "wave-function" ($\Psi$) is treated as an emergent macroscopic phenomenon, not a fundamental entity.

By running the simulation across different density scales, the engine visually proves the **Law of Large Numbers**:

* **Low-Density Regime (10,000 Photons):** The corpuscular nature dominates. Individual deterministic impacts appear stochastic and noisy ("Shot Noise"). In Experiment D, the distinct separation of the two spin states is visibly granular.
* **Fluid Regime (50,000,000 Photons):** As the computational limit scales, the chaotic individual events are subsumed into the smooth density distributions predicted by Born's Law. The interference fringes (Quadrants B and C) and the Stern-Gerlach split (Quadrant D) perfectly stabilize into harmonious statistical curves.

This observation validates the core premise of the experiment: the probability wave is simply the final resting density of millions of deterministically guided corpuscles "surfing" a viscous medium.

---

## 💻 The Hydro-Quantum Processing Unit (HQPU)

![hqpu_leitura_qnd](analytics/hqpu_leitura_qnd.png)

The second computational module of this repository (`hqpu.rs`) models the **HQPU** architecture, representing a paradigm shift from probabilistic computing to deterministic hydrodynamic logic. It encodes information in the topological stability of double-cone fluidic vortices.

* **The Vortex Qubit:** A stable vortex retaining structural integrity due to extreme equatorial kinetic energy. (A bit is represented by $\pm\omega$).
* **Fluidic Logic Gates:** Processing occurs when Vortex Qubits traverse physical obstacles within the vacuum mesh, guided by fluid-boundary mechanics and the Quantum Magnus Effect.
* **Quantum Non-Demolition (QND) Reading:** Instead of triggering a "wave-function collapse", we use high-precision analytical barometers positioned parallel to the trajectory. They measure the continuous barometric pressure of the thermodynamic wake generated by the vortex's spinning equator, reading the logical state without destroying the core's integrity.

---

## 🛠️ Compilation and Execution

Ensure you have the Rust toolchain and Vulkan/DirectX (WebGPU) drivers installed. The Python scripts in the `analytics` folder require `pandas` and `matplotlib`.

### 1. Run the Photometric Simulator (4-Quadrant Matrix)

This module dispatches up to 50 million photons to the GPU in batches processed via Compute Shaders.

```bash
cargo run --release --bin deterministic_wave_engine

```

*(Note: Ensure the binary name in `Cargo.toml` under `[[bin]]` matches "dwe" or your project's root name)*
**Output:** Generates four CSV datasets (`result_A_no_memory.csv`, `result_B_pfleegor_mandel.csv`, `result_C_magnus_spin.csv`, `result_D_single_laser.csv`).

### 2. Run the Hong-Ou-Mandel Simulator

![matrix_4_possibilities](analytics/matrix_4_possibilities.png)

This module computes the topological scattering matrix of vortex pairs across four distinct coherence and phase states.
In the continuous thermodynamic inelastic collision at a permeable dense mirror (modeled on a 2D grid as a 50/50 beam splitter), precisely synchronized twin vortices fired from opposite emitters are intercepted. If these entities were classical rigid bodies, they would interact chaotically and scatter independently, strictly adhering to a constant-density Maxwell-Boltzmann statistical distribution ($0.25$ transmission-transmission, $0.25$ reflection-reflection, and $0.50$ transmission-reflection).However, if the dynamic repulsive gradients of the inter-vortex compression zones—governed purely by strict Newtonian fluid mechanics within the WGSL shader—geometrically induce a mirror-symmetry repulsion block, the macroscopic outcome changes completely. This acoustic block invariably unifies both topological solitons, forcing them into parallel spatial drafts directed exclusively toward the same unobstructed output channel. Demonstrating this exceptionless bunching effect definitively establishes the mathematical equivalence between Bose-Einstein statistical behavior and aerodynamic collision geometry in a highly compressible viscoelastic state. Ultimately, it proves a universal physical integrity, demonstrating that quantum indistinguishability can emerge directly from deterministic classical frameworks previously thought to be obsolete.

```bash
cargo run --release --bin hong_ou_mandel

```

**Output:** Generates the continuous trajectory dataset `output.csv`.

### EPR Paradox Experiment Achieving $S=4.0$ (The PR Box)

![epr_spectral_plot](analytics/epr_spectral_plot.png)

The simulation has materialized a hypothetical PR Box (Popescu-Rohrlich Box) strictly through fluid mechanics and the Detection Loophole. The exact value of $S = 4.0$ was obtained through the CHSH equation extraction within the simulation.

The mechanism relies on the physical severity of the measurement instrument rather than "spooky action at a distance." In the WGSL compute shader, the `apply_polarizer` function exerts direct mechanical resistance. The geometric severity of this filter (the "Death Zone") is so absolute that for any intermediate angle (such as **22.5°**), the filter annihilates any particle that could cause a statistical disagreement. When the thermodynamic stress limit exceeds the particle's structural resilience (`transverse_phase`), the particle is physically destroyed (status `-2.0`). Consequently, the only survivors computed in the final statistical evaluation are the pairs that agree (or disagree) 100% of the time. This structural exclusion creates the perfect correlation that achieves the absolute theoretical limit of apparent non-locality using strictly local physics.

### The Historical Context and the EPR Paradox

When Albert Einstein, Boris Podolsky, and Nathan Rosen formulated the EPR Paradox in 1935, they anticipated the existence of "local hidden variables." However, they could not formulate the exact mechanics of how anomalous correlation survived spatial filters. At the time, physicists lacked the computational power to model non-linear fluid dynamics, chaos theory, or topological solitons in an active vacuum.

Later, Bell's Theorem relied heavily on the "Fair Sampling" assumption, mathematically presuming that detectors do not play a selective, destructive role. Einstein could not mathematically demonstrate what the DWE codebase proves: the physical sensor does not extract a fair sample. The polarizer acts as a brutal restriction furnace that physically filters the data obliquely, generating perfectly synchronized correlation as a stochastic byproduct of survivorship bias.

### The Origin of the Quantum Limit (2.82) via Environmental Losses

While the classical wave engine obtained a perfect square wave equivalent to $S = 4.0$ , real quantum laboratory experiments stall at the Tsirelson bound of approximately **2.828**.

The reason for this discrepancy lies in the core logic of the particles' structural resilience. In the Rust code, the vortex's `transverse_phase` at birth is defined as a pure linear random number. While valid in a perfect vacuum or pure abstract mathematics, the real physical world of hydrodynamics dictates that the energy density of a vortex or droplet is not linear. Instead, it assumes a bell shape (a Gaussian distribution) or a radial decay.

The observed experimental limit of **2.82** is the inevitable result of continuous dissipative friction. In a real viscoelastic medium, the environment unevenly consumes mechanical energy as the particle travels, naturally curving the perfect square wave of $S = 4.0$ into the natural cosine wave observed in standard quantum mechanics. Therefore, the quantum limit of **2.828** is essentially the absolute limit of local classical mechanics (4.0) dampened by non-recoverable thermodynamic losses present in fluid physics.

```bash
cargo run --release --bin epr

```
### 4. Run the HQPU Simulation (QND Reading)

This module processes the passage of a Soliton Qubit through the analytical fluid gate.

```bash
cargo run --release --bin hqpu

```

**Output:** Generates the thermodynamic sensor log `analytics/hqpu_readings.csv`.

### 4. Generate High-Resolution Scientific Plots (Python)

To visualize the results with academic formatting and a clean white background, execute the scripts:

```bash
# Render the 4 Quadrants of the Pfleegor-Mandel / Stern-Gerlach experiments
python analytics/plot_pfleegor_mandel.py

# Render the 4 Possibilities Topological Matrix for the HOM Effect
python plot_hong.py

# Render the HQPU Vacuum Barometry Reading
python analytics/plot_hqpu_qnd.py

```

---

## Intellectual Property & License

This theoretical model, its mathematical formulation, and the accompanying source code are the original intellectual property of Fernando B Couto. Released under the GNU General Public License v3.0 (GPL-3.0). Derivative works, academic publications, or software incorporating this algorithm must remain open-source and explicitly credit the original author. Commercial enclosure is strictly prohibited.

```

```