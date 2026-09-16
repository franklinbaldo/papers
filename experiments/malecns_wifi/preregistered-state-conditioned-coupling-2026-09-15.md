# Preregistered exploratory test — state-conditioned peer coupling

Date: 2026-09-15

Motivation: prior scalar-reliability experiments show strong seed dependence. A fixed peer-coupling weight can help substantially in some initial states and hurt in others. The next hypothesis is therefore state-dependent: peer teaching should be modulated by the current MaleCNS state rather than by one global lambda.

## Fixed backbone

- six semantic channels: MiniLM/E5 × scales 8/32/128;
- one independent trainable adapter/flavour per channel;
- fixed per-channel reliability estimated from training bytes only before learning;
- reliability-weighted leave-one-channel-out peer teacher;
- no inference-time router/attention;
- same MaleCNS reservoir, translators, optimiser, learning rate, anchor penalty, and cached frozen semantic fields as the preceding coupling-strength experiments.

## Fresh seeds

`20261004, 20261005, 20261006, 20261007`

## Arms

For every seed, with identical initialization:

1. `independent`: no peer term.
2. `static_0.50`: scalar reliability-weighted peer coupling with fixed lambda=0.50.
3. `state_uncertainty`: effective lambda for each training example is

   `lambda_eff = 0.50 * mean(4 * p_state * (1 - p_state))`

   where `p_state = sigmoid(taste_logits.detach())` is decoded from the current recurrent MaleCNS state. Thus coupling is strongest when the current brain state is uncertain and vanishes as it becomes confident.
4. `state_reward_error`: effective lambda for each training example is

   `lambda_eff = 0.50 * mean(abs(target - p_state))`

   using training reward/target only. This asks whether peer teaching should increase when the current state is wrong relative to the available reward.

Neither adaptive rule may inspect validation data, final AUPRC, seed-level outcomes, or future epochs. The gate is recomputed online from the current training state only.

## Primary outputs

Final `all_direct / unseen_generalization` and `all_direct / all` AUPRC, plus the realised lambda distribution per epoch and arm.

## Exploratory support rule

A state-conditioned arm is promoted to a fresh-seed confirmation only if all hold:

- it beats `static_0.50` on unseen generalization on at least 3 of 4 seeds;
- mean `(state_unseen - static_unseen) > 0`;
- mean `(state_unseen - independent_unseen) >= +0.03`;
- mean `(state_all - independent_all) >= -0.02`.

No rule changes after observing outcomes.

## Interpretation

This experiment tests state-conditioned plasticity, not a better global hyperparameter. A negative result rejects only these two simple gates; it does not reject the broader hypothesis that peer teaching should depend on internal state.
