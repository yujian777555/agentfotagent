from pathlib import Path

p = Path("experiments/metabox/agent_assisted_ec/lshade_reimpl.py")
t = p.read_text(encoding="utf-8")
start = t.find("            n_hist.append(N)\n            # state-triggered N+I")
end = t.find("            gen += 1", start)
assert start > 0 and end > start, (start, end)
new_block = '''            n_hist.append(N)
            # state-triggered N+I (in addition to linear schedule)
            if trigger_mode == "state":
                succ_frac = successes / max(1, N)
                stall = stall + 1 if succ_frac < theta_s else 0
                div = float(np.mean(np.std(pop, axis=0))) if N > 1 else 0.0
                divs.append(div)
                R = float(np.quantile(divs[-20:], 0.2)) if len(divs) >= 5 else 0.0
                fire = (stall >= stall_len or (len(divs) >= 5 and div < R)) and (gen - last_iv_gen) >= gen_reset_min
                if fire:
                    ev = {"gen": gen, "fes_at_event": fes, "N_before": N, "do_N": use_N, "do_I": use_I,
                          "trigger": "state"}
                    if use_N:
                        new_N = max(n_min, int(N * 0.7))
                        ev["N_after_shrink"] = new_N
                        ev["effective_shrink"] = new_N < N
                        if new_N < N:
                            orderf = np.argsort(fit)[:new_N]
                            pop = pop[orderf].copy()
                            fit = fit[orderf].copy()
                            N = new_N
                    else:
                        ev["N_after_shrink"] = N
                        ev["effective_shrink"] = False
                    n_imm = 0
                    if use_I and N > 1:
                        n_imm = min(max(1, int(0.1 * N)), max_fes - fes)
                        if n_imm > 0:
                            imm = rng.uniform(lb, ub, size=(n_imm, dim))
                            imm_fit = np.asarray([counting(ind) for ind in imm], dtype=np.float64)
                            fes += n_imm
                            orderf = np.argsort(fit)
                            keep = orderf[: max(1, N - n_imm)]
                            pop = np.vstack([pop[list(keep)], imm])
                            fit = np.concatenate([fit[list(keep)], imm_fit])
                            N = pop.shape[0]
                    ev["n_immigrants"] = n_imm
                    ev["N_after_immigration"] = N
                    events.append(ev)
                    best_hist[-1] = float(min(best_hist[-1], np.min(fit)))
                    last_iv_gen = gen
                    stall = 0
'''
t = t[:start] + new_block + t[end:]
p.write_text(t, encoding="utf-8")
print("patched")
