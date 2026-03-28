# EcoFlight AI -- Research bibliography (for judges / Q&A)

Use this file when judges ask "what literature did you build on?" Most hackathon teams cite nothing. You cite **specific research lines**.

---

## 1. Contrails vs CO2 (why dual optimization matters)

- **Lee et al.** and IPCC-aligned assessments: aviation effective radiative forcing splits between **CO2 and non-CO2** (contrail cirrus is a large share of near-term warming).
- **Talking point:** "We optimize **total climate impact**, not fuel alone. Fuel-only misses contrail cirrus."

---

## 2. Operational contrail avoidance (proof it works in the real world)

- **Google Research + American Airlines + Breakthrough Energy** trials (2023--2025): AI-guided vertical/lateral shifts, large contrail reduction, **small fuel penalty** on flights that flew the avoidance.
- **Talking point:** "This is not science fiction -- Google and AA already flight-tested it."

---

## 3. 4D trajectory + contrails (your "4D" story)

- **ENAC (HAL)** -- *Fast Marching Tree* for **4D** cruise trajectories in **contrail-sensitive** environments; treats favorable-contrail regions as **soft obstacles** that evolve in time.
- **Talking point:** "Our demo uses a **climate corridor** (lateral S-curve) plus **vertical** contrail avoidance -- same *idea* as FMT contrail routing, simplified for a hackathon."

---

## 4. Feasibility and limits (shows maturity)

- **arXiv 2504.13907 (2025)** -- *Contrail, or not contrail, that is the question: the feasibility of climate-optimal routing* -- discusses forecast uncertainty, capacity, operations.
- **Talking point:** "We know uncertainty matters; production would ingest **NOAA / radiosonde / ensemble** humidity. The demo uses a regional model."

---

## 5. Predict-then-optimize for fuel

- **TRB / transportation research (2025)** -- predict-then-optimize minimizing aircraft fuel using QAR-style data; reported **~few percent** fuel improvements vs actuals.
- **Talking point:** "Our stack is the same *pattern*: predict burn, then optimize trajectory."

---

## 6. Wind-coupled / bi-level trajectory optimization

- **Springer, Optimization and Engineering (2025)** -- bi-level aircraft trajectory optimization under **unsteady wind**.
- **Talking point:** "We couple **wind** into groundspeed and segment time for the **4th dimension** (ETA along track)."

---

## 7. Open tooling ecosystem

- **OpenAP** handbook -- contrail optimization chapter (`openap.dev`).
- **Talking point:** "We align with open contrail-aware trajectory research tooling."

---

## 8. Full-mission optimal control (climb / cruise / descent)

- ENAC / aerospace journals on **holistic** trajectory optimization (single optimal control problem across phases).
- **Talking point:** "We show **climb -- cruise step -- CDO-style descent**, not a flat cruise-only line."

---

## How EcoFlight is *different* from a generic GPT fuel router

| Generic team | EcoFlight |
|--------------|-----------|
| 2D map, one line | **3D paths on a globe** + altitude encoded |
| Fuel % only | **Fuel + contrail CO2-eq** |
| No time | **Per-waypoint ETA (4D)** |
| No citations | **This document + API `research_references`** |

---

*Last updated: hackathon build. Verify URLs before citing in academic work.*
