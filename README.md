# 🌙 MoonBase v2.2.0

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://moonbase.streamlit.app)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/moonbase?style=social)](https://github.com/YOUR_USERNAME/moonbase)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![NASA LRO Data](https://img.shields.io/badge/Data-NASA%20LRO-cyan)](https://www.nasa.gov/mission/lro/)
[![Artemis Aligned](https://img.shields.io/badge/Mission-Artemis%20Aligned-pink)](https://www.nasa.gov/artemis/)

> **Lunar Site Selection & Sweet Spot Analysis for Artemis-Era Missions**

MoonBase is an interactive, data-driven tool that scores and compares candidate lunar base locations using real **NASA LRO (Lunar Reconnaissance Orbiter)** datasets. Built with Streamlit, Folium, and Plotly, it provides a mission-control-style interface for evaluating illumination, ice access, terrain safety, thermal conditions, and subsurface access across 14+ candidate sites.
<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>
---

🚀 **Try it now:** [https://moonbase.streamlit.app](https://moonbase.streamlit.app)
<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>
---

## 🛰️ Features

### Core Analysis
- **Interactive NASA LRO WAC Mosaic Map** — Click anywhere on the Moon to generate a custom site analysis instantly.
- **7-Criteria Weighted Scoring Engine** — Illumination (20%), Ice Access (20%), Subsurface Access (20%), Slope Safety (15%), Temperature (10%), Regolith (10%), Comms (5%).
- **14 NASA Candidate Sites** — Pre-loaded with real data for Artemis III candidates including Shackleton Crater Rim, Connecting Ridge, de Gerlache Rim, Mons Mouton, and more.
- **Seasonal Illumination Model** — Accounts for the 18.6-year lunar nodal cycle drift (2026–2034).

### Advanced Tooling
- **⚖️ Compare Mode** — Side-by-side comparison of up to 3 sites with a Plotly radar chart and automatic 🏆 winner selection.
- **🛰️ Artemis III Overlay** — Toggle official NASA Artemis III candidate landing regions directly on the map.
- **⛰️ Elevation Cross-Section** — 50 km synthetic terrain profile based on the site's measured slope for lander approach visualization.
- **💧 ISRU Water Production Calculator** — Estimate daily water output (L/day) from regolith processing based on ice confidence.
- **☢️ Radiation Shield Depth Calculator** — Compute required regolith overburden to reach target radiation doses (10–400 mSv/year).
- **🌅 Sun Position Animation** — Visualize illumination and temperature changes across a full 29.5-day lunar day.
- **🧪 Simulation Lab** — What-if analysis for crew size, habitat mass, and power source (Solar/Hybrid/Nuclear).
- **💾 Persistent Memory** — SQLite-backed analysis history that survives page refreshes.
- **🛰️ Live Solar System Tracker** — Embedded NASA Eyes on the Solar System feed.
<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>
---

## 🧪 Data Sources

| Metric | Source |
|--------|--------|
| Illumination | LRO LOLA |
| Ice Confidence | Mini-RF + LCROSS |
| Slope | LOLA DEM |
| Temperature | Diviner |
| Regolith Depth | Mini-RF |
| Subsurface Access | LRO LROC |
| Base Map | NASA LRO WAC Global Mosaic (303 ppd) |

---

## 🛠️ Tech Stack

- **Framework:** Streamlit
- **Maps:** Folium + streamlit-folium
- **Charts:** Plotly
- **Data:** Pandas, NumPy
- **Storage:** SQLite
- **APIs:** NASA LRO Tile Server, NASA Eyes on the Solar System
If you find MoonBase useful or just want to support future space data projects:

<a href="https://buymeacoffee.com/stargazex" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" > </a>
---

