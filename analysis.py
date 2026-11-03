"""
Assignment 1: Does lower volatility really mean a safer mutual fund?
Category: Flexi Cap (Direct, Growth). Window: 1 Nov 2019 - 30 Oct 2026 (7 years).
Data: AMFI daily NAVs via github.com/captn3m0/historical-mf-data (funds.db).
Benchmark: Motilal Oswal Nifty 500 Index Fund - Direct (Nifty 500 TRI proxy).
"""
import sqlite3, json
import numpy as np, pandas as pd

DB = "/home/claude/data/funds.db"
START, END = "2019-11-01", "2026-10-30"
FUNDS = {
    122639: "Parag Parikh", 118955: "HDFC", 120166: "Kotak", 120843: "quant",
    118535: "Franklin India", 118275: "Canara Robeco", 120662: "UTI", 129046: "Motilal Oswal",
}
BENCH = {147625: "Nifty 500 (index fund)"}
ANN = 252

def load():
    codes = {**FUNDS, **BENCH}
    c = sqlite3.connect(DB)
    q = f"select scheme_code, date, nav from nav where scheme_code in ({','.join(map(str, codes))}) and date between '{START}' and '{END}'"
    df = pd.read_sql(q, c)
    df["date"] = pd.to_datetime(df.date); df["nav"] = pd.to_numeric(df.nav, errors="coerce")
    p = df.pivot_table(index="date", columns="scheme_code", values="nav").rename(columns=codes)
    return p.dropna()  # common dates only

def drawdown(nav):
    return nav / nav.cummax() - 1

def mdd_stats(nav):
    dd = drawdown(nav)
    trough = dd.idxmin(); peak = nav[:trough].idxmax()
    rec = nav[trough:][nav[trough:] >= nav[peak]]
    rec_date = rec.index[0] if len(rec) else pd.NaT
    return dict(mdd=dd.min(), peak=peak.date(), trough=trough.date(),
                recovery=None if pd.isna(rec_date) else rec_date.date(),
                days_to_recover=None if pd.isna(rec_date) else (rec_date - trough).days,
                underwater_days=None if pd.isna(rec_date) else (rec_date - peak).days)

def capture(fm, bm, down=True):
    """Morningstar-style geometric capture on monthly returns."""
    mask = bm < 0 if down else bm > 0
    f, b = fm[mask], bm[mask]
    gf = np.prod(1 + f) ** (1 / len(f)) - 1
    gb = np.prod(1 + b) ** (1 / len(b)) - 1
    return gf / gb

def metrics(p, bench):
    r = p.pct_change().dropna()
    m = p.resample("ME").last().pct_change().dropna()
    yrs = (p.index[-1] - p.index[0]).days / 365.25
    out = {}
    for f in p.columns:
        ri, nav = r[f], p[f]
        dd = drawdown(nav)
        down = ri[ri < 0]
        cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
        vol = ri.std() * np.sqrt(ANN)
        dsd = np.sqrt((np.minimum(ri, 0) ** 2).mean()) * np.sqrt(ANN)
        cov = np.cov(ri, r[bench])
        out[f] = dict(
            cagr=cagr, vol=vol, downside_dev=dsd,
            sharpe_like=(cagr - 0.06) / vol,             # 6% ~ avg T-bill over window
            sortino_like=(cagr - 0.06) / dsd,
            beta=cov[0, 1] / cov[1, 1],
            ulcer=np.sqrt((dd ** 2).mean()),
            worst_day=ri.min(), worst_month=m[f].min(),
            cvar5_daily=ri[ri <= ri.quantile(0.05)].mean(),
            down_capture=capture(m[f], m[bench], True),
            up_capture=capture(m[f], m[bench], False),
            pct_months_beat_in_down=(m[f][m[bench] < 0] > m[bench][m[bench] < 0]).mean(),
            **mdd_stats(nav),
        )
    return pd.DataFrame(out).T, r, m

def stress_episodes(p, bench, thresh=-0.10):
    """Benchmark peak-to-trough episodes deeper than thresh."""
    nav = p[bench]; dd = drawdown(nav)
    eps, in_ep = [], False
    for d, v in dd.items():
        if not in_ep and v < 0:
            in_ep, start = True, nav[:d].idxmax()
        if in_ep and v == 0:
            seg = dd[start:d]
            if seg.min() <= thresh:
                eps.append((start, seg.idxmin()))
            in_ep = False
    if in_ep and dd[start:].min() <= thresh:
        eps.append((start, dd[start:].idxmin()))
    rows = {}
    for s, t in eps:
        key = f"{s:%b %Y} - {t:%b %Y}"
        rows[key] = (p.loc[t] / p.loc[s] - 1)
    return pd.DataFrame(rows)

def rolling(p, bench, win=252):
    r = p.pct_change().dropna()
    rv = r.rolling(win).std() * np.sqrt(ANN)
    return rv.dropna()

def oos_test(p, bench, split="2022-11-01"):
    """Does volatility in the first half predict losses in the second half?"""
    a, b = p[:split], p[split:]
    ma, _, _ = metrics(a, bench); mb, _, _ = metrics(b, bench)
    funds = list(FUNDS.values())
    d = pd.DataFrame({
        "vol_H1": ma.loc[funds, "vol"], "mdd_H1": ma.loc[funds, "mdd"], "dcap_H1": ma.loc[funds, "down_capture"],
        "vol_H2": mb.loc[funds, "vol"], "mdd_H2": mb.loc[funds, "mdd"], "dcap_H2": mb.loc[funds, "down_capture"],
    }).astype(float)
    return d

if __name__ == "__main__":
    bench = list(BENCH.values())[0]
    p = load()
    print("Common window:", p.index[0].date(), "->", p.index[-1].date(), "| obs:", len(p))
    M, r, m = metrics(p, bench)
    M.to_csv("metrics.csv")
    S = stress_episodes(p, bench); S.to_csv("stress.csv")
    RV = rolling(p, bench); RV.to_csv("rolling_vol.csv")
    O = oos_test(p, bench); O.to_csv("oos.csv")
    drawdown(p).to_csv("drawdowns.csv"); p.to_csv("nav.csv")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    show = M[["cagr", "vol", "downside_dev", "beta", "mdd", "peak", "trough", "recovery", "underwater_days",
              "ulcer", "down_capture", "up_capture", "worst_month", "cvar5_daily", "sortino_like"]]
    print(show.to_string(float_format=lambda x: f"{x:.3f}"))
    print("\nStress episodes (benchmark < -10%):\n", S.to_string(float_format=lambda x: f"{x:.1%}"))
    print("\nOOS:\n", O.to_string(float_format=lambda x: f"{x:.3f}"))
    print("\nOOS Spearman:\n", O.corr("spearman").loc[["vol_H1", "mdd_H1", "dcap_H1"], ["vol_H2", "mdd_H2", "dcap_H2"]].round(2))

def extra(p, bench):
    """Post-COVID MDD, longest underwater spell, current drawdown, rank tables."""
    rows = {}
    post = p["2021-01-01":]
    for f in p.columns:
        dd = drawdown(p[f])
        at_peak = dd.index[dd == 0]
        # calendar days between consecutive new highs (and from last high to end of window)
        gaps = pd.Series(list(at_peak[1:]) + [dd.index[-1]]) - pd.Series(at_peak)
        m = mdd_stats(post[f])
        rows[f] = dict(mdd_post2021=m["mdd"], mdd_post2021_trough=m["trough"],
                       longest_underwater_days=int(gaps.max().days),
                       current_dd=dd.iloc[-1])
    return pd.DataFrame(rows).T

if __name__ == "__main__":
    E = extra(p, bench); E.to_csv("extra.csv")
    print("\n", E.to_string())
    funds = list(FUNDS.values())
    A = M.loc[funds, ["vol", "mdd", "ulcer", "down_capture", "cvar5_daily", "worst_month"]].astype(float).join(E.loc[funds, ["mdd_post2021", "longest_underwater_days"]].astype(float))
    # rank 1 = safest
    R = pd.DataFrame({
        "SD": A.vol.rank(), "Max DD": (-A.mdd).rank(), "Post-2021 DD": (-A.mdd_post2021).rank(),
        "Ulcer": A.ulcer.rank(), "Down capture": A.down_capture.rank(),
        "Longest underwater": A.longest_underwater_days.rank(),
    }).astype(int)
    R.to_csv("ranks.csv"); print("\nRanks (1=safest):\n", R.sort_values("SD").to_string())
    print("\nSpearman between metric rankings:\n", R.corr("spearman").round(2).to_string())
    rvr = RV[funds].rank(axis=1)
    print("\nRolling-1y vol rank stats (1=lowest vol):\n", rvr.describe().loc[["mean", "min", "max"]].round(1).to_string())
    print("share of days each fund was lowest-vol:\n", (rvr == 1).mean().round(2).to_string())
