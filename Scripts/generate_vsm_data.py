# scripts/generate_vsm_data.py
import pandas as pd
import os
from collections import Counter

def generate_vsm_data_from_csv(csv_path, state_filter=None, user_filter=None, min_freq=0):
    min_freq = int(min_freq)

    # ✅ Make sure this is inside the function!
    df = pd.read_csv(csv_path, low_memory=False)
    df = df[['CLCL_CLAIM_ID', 'WMHS_ROUTE_DT', 'WQDF_DESC3', 'State', 'USUS_USR_ID']].dropna()
    df['WMHS_ROUTE_DT'] = pd.to_datetime(df['WMHS_ROUTE_DT'], errors='coerce')

    if state_filter:
        df = df[df['State'] == state_filter]
    if user_filter:
        df = df[df['USUS_USR_ID'] == user_filter]

    df = df.sort_values(by=['CLCL_CLAIM_ID', 'WMHS_ROUTE_DT'])

    edges = []
    node_counter = Counter()

    for claim_id, group in df.groupby('CLCL_CLAIM_ID'):
        steps = group['WQDF_DESC3'].tolist()
        for step in steps:
            node_counter[step] += 1
        edges.extend([(steps[i], steps[i+1]) for i in range(len(steps) - 1)])

    edge_counts = Counter(edges)

    nodes = [node for node in node_counter if node_counter[node] >= int(min_freq)]
    node_set = set(nodes)

    elements = []

    for node in nodes:
        freq = node_counter[node]
        color = get_color_by_frequency(freq)
        elements.append({ "data": { "id": node, "label": node, "freq": freq, "color": color } })

    for (src, tgt), weight in edge_counts.items():
        if src in node_set and tgt in node_set:
            elements.append({ "data": { "source": src, "target": tgt, "label": str(weight) } })

    return elements

def generate_bottleneck_table(mode="time_to_next"):
    # Load the CSV — adjust path if needed
    # csv_path = r"D:\Office Works\VSC\Diagram Template\ProcessMining\Abbyy Timeline Jan-Dec 2024 CO MO TX 2.csv"
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data.csv"))
    print(f"Loading CSV from: {csv_path}")

    # df = pd.read_csv(csv_path, parse_dates=["WMHS_ROUTE_DT"], low_memory=False)
    df = pd.read_csv(csv_path, low_memory=False)
    df["WMHS_ROUTE_DT"] = pd.to_datetime(df["WMHS_ROUTE_DT"], errors="coerce")


    # Filter necessary columns
    df = df[["CLCL_CLAIM_ID", "WMHS_ROUTE_DT", "WQDF_DESC3"]].dropna()
    df.sort_values(by=["CLCL_CLAIM_ID", "WMHS_ROUTE_DT"], inplace=True)

    records = []
    for claim_id, group in df.groupby("CLCL_CLAIM_ID"):
        group = group.sort_values("WMHS_ROUTE_DT")
        if mode == "time_between":
            transitions = zip(group["WQDF_DESC3"], group["WQDF_DESC3"].shift(-1), group["WMHS_ROUTE_DT"], group["WMHS_ROUTE_DT"].shift(-1))
            for from_evt, to_evt, t1, t2 in transitions:
                if pd.notna(from_evt) and pd.notna(to_evt) and pd.notna(t1) and pd.notna(t2):
                    time_diff = (t2 - t1).total_seconds() / 3600  # in hours
                    event = f"{from_evt} -> {to_evt}"
                    records.append((event, time_diff))
        else:  # time_to_next
            for evt, t1, t2 in zip(group["WQDF_DESC3"], group["WMHS_ROUTE_DT"], group["WMHS_ROUTE_DT"].shift(-1)):
                if pd.notna(evt) and pd.notna(t1) and pd.notna(t2):
                    time_diff = (t2 - t1).total_seconds() / 3600
                    records.append((evt, time_diff))

    # Aggregate
    df_result = pd.DataFrame(records, columns=["event", "duration"])
    grouped = df_result.groupby("event").agg(
        count=("duration", "count"),
        avg_time_h=("duration", "mean"),
        total_time_h=("duration", "sum")
    ).reset_index()

    grouped["per_timeline"] = grouped["count"] / df["CLCL_CLAIM_ID"].nunique()
    grouped["new_time_h"] = None  # Placeholder
    total_time = grouped["total_time_h"].sum()
    grouped["total_time_pct"] = grouped["total_time_h"] / total_time * 100

    # Format output for JSON
    output = grouped.to_dict(orient="records")
    return output

def get_color_by_frequency(freq):
    if freq > 1000:
        return "#e74c3c"  # red
    elif freq > 500:
        return "#f39c12"  # orange
    elif freq > 100:
        return "#27ae60"  # green
    else:
        return "#2980b9"  # blue

def get_unique_states_and_users(csv_path):
    df = pd.read_csv(csv_path, low_memory=False)
    states = sorted(df['State'].dropna().unique().tolist())
    users = sorted(df['USUS_USR_ID'].dropna().unique().tolist())
    return states, users
