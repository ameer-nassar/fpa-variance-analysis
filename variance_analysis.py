# variance_analysis.py  –  FP&A Variance Dashboard
# -------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
from matplotlib.patches import Patch   # needed for heatmap legend

# ---------- Load Data ----------
df = pd.read_csv("fpa_variance_data_monthly.csv")

# ---------- Helpers ----------
def format_millions_2dp(val: float) -> str:
    return f"${val / 1e6:.2f}M"

# ===========================================
# PLOT 1 : Total Budget vs Actuals by Department
# ===========================================

dept_summary = df.groupby("Department")[["Budget", "Actual"]].sum().reset_index()
x = np.arange(len(dept_summary))
bar_w = 0.35

plt.figure(figsize=(12, 6))
b1 = plt.bar(x - bar_w/2, dept_summary["Budget"], width=bar_w,
             label="Budget", color="#FF8C00") # Budget = left (orange)

b2 = plt.bar(x + bar_w/2, dept_summary["Actual"], width=bar_w,
             label="Actual", color="#4682B4") # Actual = right (blue)

ax = plt.gca()
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${int(x):,}'))
plt.xticks(x, dept_summary["Department"], rotation=15, ha='right')
plt.ylabel("Total ($)")
plt.title("Total Budget vs Actuals by Department")
plt.legend()

# Annotate bars
for bar in (*b1, *b2):
    h = bar.get_height()
    plt.annotate(format_millions_2dp(h),
                 (bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 7), textcoords="offset points",
                 ha='center', fontsize=7.5, weight='bold')

plt.tight_layout()
plt.savefig("plot1_total_actuals_vs_budget.png", dpi=300)
plt.close()

# =================================================
# PLOT 2 • Average Variance %  (bar)
# =================================================
bar_data = (df.groupby("Department")["Variance_pct"]
              .mean()
              .mul(100)           # convert → %
              .reset_index())

plt.figure(figsize=(10, 6))
sns.barplot(data=bar_data, x="Department", y="Variance_pct", hue="Department", palette="viridis", legend=False)
plt.axhline(0, color="gray", ls="--", lw=1)
plt.ylim(-8, 8)
plt.ylabel("Average Variance (%)")
plt.title("Average Variance % by Department")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("plot2_avg_variance_bar_chart.png", dpi=300)
plt.close()

# =================================================
# PLOT 3 • Facet Grid (month-by-month lines)
# =================================================
df["Month"] = pd.to_datetime(df["Month"])  # Parse ISO format
facet_df = df.assign(
    Variance_pct=df["Variance_pct"].mul(100),
    Month_Num=df["Month"].dt.month
)

g = sns.FacetGrid(facet_df, col="Department", col_wrap=4, height=3.2, sharey=True)
g.map(sns.lineplot, "Month_Num", "Variance_pct", marker="o", color="orange")
g.set_titles("{col_name}")
g.set_axis_labels("", "Variance (%)")
for ax in g.axes.flatten():
    ax.axhline(0, color='gray', ls='--', lw=0.8)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(range(1, 13), fontsize=8)
g.fig.suptitle("Monthly Variance % by Department", fontsize=14)
g.tight_layout()
g.fig.subplots_adjust(top=0.88)
g.savefig("plot3_faceted_lines.png", dpi=300)

# =================================================
# PLOT 4 • Heatmap Jan-Dec  (+/-) with legend
# =================================================
df["Month_Label"] = df["Month"].dt.strftime("%b")
df["Month_Label"] = pd.Categorical(df["Month_Label"],
                                   categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                                   ordered=True)

heat = df.pivot(index="Department", columns="Month_Label", values="Variance_pct")

plt.figure(figsize=(12, 6))
ax = sns.heatmap(heat*100, annot=True, fmt="",
                 cmap="coolwarm", center=0,
                 annot_kws={"fontsize":9},
                 cbar_kws={'label': 'Variance (%)'})
ax.set_xlabel("Month")

for t in ax.texts:
    t.set_text(f"{float(t.get_text()):+0.1f}")

plt.title("Heatmap of Monthly Variance % (Jan–Dec)", pad=20)
legend_handles = [Patch(fc='red', ec='red', label='Over Budget (+)'),
                  Patch(fc='blue', ec='blue', label='Under Budget (–)')]
plt.legend(handles=legend_handles, loc='upper center',
           bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, title="Legend")
plt.tight_layout()
plt.savefig("plot4_heatmap_variance_pct.png", dpi=300)
plt.close()

# =================================================
# PLOT 5 • Variance Distribution (boxplot, %)
# =================================================
plt.figure(figsize=(12, 6))
ax = sns.boxplot(data=df, x="Department", y="Variance_pct", color="#2a80b9")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x*100:+.0f}%")) # Format Y-axis as percentage with +/- sign
plt.ylabel("Variance (%)", labelpad=10) # Set axis labels and title
plt.title("Distribution of Monthly Variance % by Department", pad=15) # Set axis labels and title
plt.tight_layout()
plt.savefig("plot5_boxplot_variance_pct.png", dpi=300)
plt.close()

# =================================================
# EXECUTIVE SUMMARY (prints + writes to file)
# =================================================
tot_bud  = df["Budget"].sum()
tot_act  = df["Actual"].sum()
tot_var  = tot_act - tot_bud
tot_var_pct = tot_var / tot_bud

lines = [
    "========== FP&A Executive Summary ==========",
    f"Total Budget : ${tot_bud:,.0f}",
    f"Total Actual : ${tot_act:,.0f}",
    f"Total Variance: {tot_var:+,.0f} USD ({tot_var_pct:+.2%})",
    ""
]

dept_sum = (df.groupby("Department")[["Budget","Actual"]]
              .sum()
              .assign(Variance=lambda d: d["Actual"]-d["Budget"],
                      Variance_pct=lambda d: d["Variance"]/d["Budget"]))

for _, r in dept_sum.iterrows():
    dirn = "under" if r["Variance"] < 0 else "over"
    lines.append(f"{r.name:<17} is {abs(r['Variance_pct'])*100:5.1f}% {dirn} budget "
                 f"({r['Variance']:+,.0f} USD)")

print("\n".join(lines))

with open("executive_summary.txt", "w") as f:
    f.write("\n".join(lines))

print("\nAll plots and summary files generated successfully.")
