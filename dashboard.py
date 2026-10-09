from __future__ import annotations
import json
from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="TLT ↔ QQQ Holdings Weekly Lead/Lag", layout="wide")
cfg = json.loads(Path("config.json").read_text())

@st.cache_data(ttl=60)
def load_latest():
    con = sqlite3.connect(cfg["database"])
    table = cfg["analysis_table"]
    df = pd.read_sql_query(f"""
        SELECT * FROM {table}
        WHERE asof_date=(SELECT MAX(asof_date) FROM {table})
    """, con)
    con.close()
    return df

df = load_latest()
st.title("TLT ↔ QQQ Holdings Weekly Relationship")
st.caption("Rolling weekly correlation + 0–6 week TLT lead analysis. Positive score = moves with TLT; negative = inverse.")

if df.empty:
    st.warning("No analysis rows yet. Run: python ibkr_backfill.py  then  python analyze_weekly.py")
    st.stop()

asof = df["asof_date"].max()
alerts = int(df["follower_alert"].fillna(0).sum())
c1,c2,c3,c4 = st.columns(4)
c1.metric("As of", asof)
c2.metric("QQQ stocks", len(df))
c3.metric("Follower alerts", alerts)
c4.metric("Strong lead relations", int(((df["best_lag"] >= 1) & (df["best_lag_corr"].abs() >= .45)).sum()))

tab1,tab2,tab3,tab4 = st.tabs(["Leadership Board","Follower Alerts","Lag Matrix","Symbol Detail"])

with tab1:
    top_n = st.selectbox("Display", [25,50,100,250,500], index=1)
    sort_mode = st.radio("Sort", ["Strongest relationship","Positive TLT","Inverse TLT"], horizontal=True)
    work = df.copy()
    if sort_mode == "Strongest relationship":
        work["sort_key"] = work["relationship_score"].abs()
        work = work.sort_values("sort_key", ascending=False).head(top_n)
    elif sort_mode == "Positive TLT":
        work = work.sort_values("relationship_score", ascending=False).head(top_n)
    else:
        work = work.sort_values("relationship_score", ascending=True).head(top_n)

    fig = px.bar(
        work, x="ticker", y="relationship_score",
        hover_data=["corr_13w","corr_26w","corr_52w","best_lag","best_lag_corr","rs_4w","rs_13w"],
        title="Signed TLT Relationship Score (-100 inverse → +100 positive)"
    )
    fig.add_hline(y=0)
    st.plotly_chart(fig, use_container_width=True)

    shown = work[[
        "ticker","relationship_score","relationship_type","corr_13w","corr_26w","corr_52w",
        "best_lag","best_lag_corr","best_lag_beta","rs_4w","rs_13w","follower_alert"
    ]].copy()
    for c in ["corr_13w","corr_26w","corr_52w","best_lag_corr","best_lag_beta","rs_4w","rs_13w"]:
        shown[c] = shown[c].round(3)
    shown["relationship_score"] = shown["relationship_score"].round(1)
    st.dataframe(shown, use_container_width=True, hide_index=True)

with tab2:
    a = df[df["follower_alert"] == 1].copy()
    if a.empty:
        st.info("No active follower alerts on the latest completed week.")
    else:
        a["expected"] = a["best_lag_beta"] * a["tlt_ret_1w"]
        a["gap_abs"] = a["lag_gap"].abs()
        a = a.sort_values("gap_abs", ascending=False)
        st.dataframe(a[[
            "ticker","best_lag","best_lag_corr","best_lag_beta","tlt_ret_1w",
            "stock_ret_1w","expected","lag_gap","expected_direction"
        ]], use_container_width=True, hide_index=True)

        fig = px.scatter(
            a, x="best_lag_corr", y="lag_gap", size="gap_abs", text="ticker",
            hover_data=["best_lag","relationship_score"],
            title="Active TLT follower gaps"
        )
        fig.add_hline(y=0)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    heat_n = st.selectbox("Heatmap rows", [25,50,100,250,500], index=1)
    lag_cols = [f"lag{i}_corr" for i in range(7)]
    mat = df.set_index("ticker")[lag_cols].copy()
    mat.columns = [f"TLT leads {i}w" for i in range(7)]
    order = df.assign(m=df["best_lag_corr"].abs()).sort_values("m",ascending=False)["ticker"]
    mat = mat.reindex(order).head(heat_n)
    fig = px.imshow(
        mat, aspect="auto", zmin=-1, zmax=1,
        labels=dict(x="Lead", y="QQQ holding", color="Correlation"),
        title="TLT lead/lag correlation heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    ticker = st.selectbox("QQQ holding", sorted(df["ticker"].tolist()))
    r = df[df["ticker"] == ticker].iloc[0]
    a,b,c,d = st.columns(4)
    a.metric("Relationship score", f"{r.relationship_score:.1f}")
    b.metric("Best TLT lead", f"{int(r.best_lag)} weeks")
    c.metric("Best lag correlation", f"{r.best_lag_corr:.3f}")
    d.metric("26W beta to TLT", f"{r.beta_26w:.3f}" if pd.notna(r.beta_26w) else "n/a")

    lagdf = pd.DataFrame({
        "lag": list(range(7)),
        "corr": [r[f"lag{i}_corr"] for i in range(7)]
    })
    fig = px.bar(lagdf, x="lag", y="corr", title=f"{ticker}: correlation when TLT leads by N weeks")
    fig.add_hline(y=0)
    st.plotly_chart(fig, use_container_width=True)

    corrdf = pd.DataFrame({
        "window":["13W","26W","52W"],
        "corr":[r.corr_13w,r.corr_26w,r.corr_52w]
    })
    fig2 = px.bar(corrdf, x="window", y="corr", title=f"{ticker}: rolling-window relationship with TLT")
    fig2.add_hline(y=0)
    st.plotly_chart(fig2, use_container_width=True)
