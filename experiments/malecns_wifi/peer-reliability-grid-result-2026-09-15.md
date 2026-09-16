# Peer-reliability grid — exploratory result (2026-09-15)

Source run: `franklinbaldo/malecns-peer-reliability-grid`, GitHub Actions `34960309065`, papers ref `43aea5a67b25cf7ac3bf6599924e6b715d2bb321`.

This note records the completed exploratory grid before the follow-up replication is run.

## Fixed training reliabilities

Reliability was estimated from training bytes only, before learning, and normalized to mean 1.0.

- MiniLM / 8: 0.7729197849
- MiniLM / 32: 1.0008723119
- MiniLM / 128: 0.9457550521
- E5 / 8: 1.0540044410
- E5 / 32: 1.1326543360
- E5 / 128: 1.0937940739

## Final all-direct metrics

| arm | all AUPRC | unseen-generalization AUPRC |
| --- | ---: | ---: |
| independent | 0.4070789632 | 0.2571803377 |
| reliability λ=0.05 | 0.3545269927 | 0.2413856205 |
| reliability λ=0.10 | 0.2678757612 | 0.2158564613 |
| reliability λ=0.25 | 0.2467879285 | 0.1931051165 |
| reliability λ=0.50 | 0.3854724015 | 0.5349635676 |

The preregistered global guard allowed an all-direct/all degradation of at most 0.0200. λ=0.50 degraded by 0.0216065617, missing that guard by 0.0016065617 while improving unseen-generalization by 0.2777832299.

## Dropout observation for λ=0.50

Compared with independent, λ=0.50 also increased unseen-generalization under several missing-channel conditions:

- `minilm_short_only`: 0.2143663262 → 0.4580196545
- `no_128`: 0.1635101161 → 0.2629106605
- `no_encoder_1`: 0.2238297799 → 0.3294198370
- `no_encoder_0`: 0.2200415703 → 0.2186118080 (roughly unchanged)

This is exploratory evidence only. λ=0.50 was selected after observing this grid, so it must be replicated on new seeds before interpretation as a stable effect.
