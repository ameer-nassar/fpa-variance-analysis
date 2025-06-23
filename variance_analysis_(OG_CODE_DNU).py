import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.ticker as mtick # plot 4
from matplotlib.patches import Patch # for plot 3 (or all plots, should i remove this line here and add it back to the plot 3 area of code?)

# Helper function for label formatting
def format_millions_2dp(val):
    return f"${val / 1e6:.2f}M"

# Load data
df = pd.read_csv("fpa_variance_data_monthly.csv")

# Total Budget vs Actual by Department (Plot 1)
dept_summary = df.groupby("Department")[["Budget", "Actual"]].sum().reset_index()
x = np.arange(len(dept_summary))
bar_width = 0.35

plt.figure(figsize=(12, 6))
bars1 = plt.bar(x - bar_width/2, dept_summary["Budget"], width=bar_width, label="Budget", color="#FDB813")
bars2 = plt.bar(x + bar_width/2, dept_summary["Actual"], width=bar_width, label="Actual", color="#FF6F1F")

ax = plt.gca()
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${int(x):,}'))
plt.xticks(x, dept_summary["Department"], rotation=15, ha='right')
plt.ylabel("Total ($)")
plt.title("Total Budget vs Actual by Department")
plt.legend()

for bar in bars1:
    h = bar.get_height()
    plt.annotate(format_millions_2dp(h),
                 xy=(bar.get_x() + bar.get_width() / 2, h),
                 xytext=(0, 7), textcoords="offset points", ha='center',
                 fontsize=7.5, weight='bold')

for bar in bars2:
    h = bar.get_height()
    plt.annotate(format_millions_2dp(h),
                 xy=(bar.get_x() + bar.get_width() / 2, h),
                 xytext=(0, 7), textcoords="offset points", ha='center',
                 fontsize=7.5, weight='bold')

plt.tight_layout()
plt.savefig("plot1_total_budget_actual.png", dpi=300)
plt.close()

# Monthly Variance % by Department (Plot 2: Bar Chart – Average Variance % by Department)
bar_data = df.groupby("Department")["Variance_pct"].mean().reset_index()
bar_data["Variance_pct"] = bar_data["Variance_pct"] * 100  # to %

plt.figure(figsize=(10, 6))
sns.barplot(data=bar_data, x="Department", y="Variance_pct", palette="viridis")
plt.axhline(0, color="gray", linestyle="--", linewidth=1)
plt.ylabel("Average Variance (%)")
plt.title("Average Variance % by Department")
plt.ylim(-8, 8)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("plot2_avg_variance_bar_chart.png", dpi=300)
plt.close()

# Monthly Variance % by Department (Plot 2.5: Facet Grid – Average Variance % by Department)

# Plot 2: Facet Grid – Monthly Variance % by Department (1–12 on All Charts)

# Prepare data
month_number_map = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}
facet_data = df.copy()
facet_data["Variance_pct"] = facet_data["Variance_pct"] * 100
facet_data["Month_Num"] = facet_data["Month"].map(month_number_map)

# Build the Facet Grid
g = sns.FacetGrid(facet_data, col="Department", col_wrap=4, height=3.2, sharey=True)
g.map(sns.lineplot, "Month_Num", "Variance_pct", marker="o", color="orange")
g.set_titles("{col_name}")
g.set_axis_labels("", "Variance (%)")  # Remove "Month" label

# Force 1–12 ticks on all charts
for ax in g.axes.flatten():
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([str(i) for i in range(1, 13)], fontsize=8)
    ax.tick_params(axis='x', labelbottom=True)

g.fig.suptitle("Monthly Variance % by Department", fontsize=14)
g.tight_layout()
g.fig.subplots_adjust(top=0.88)
g.savefig("plot2.5_facet_grid.png", dpi=300)

# Heatmap of Monthly Variance % (Jan–Dec, +/- with Legend) (Plot 3)

# Ensure month order
ordered_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
df["Month"] = pd.Categorical(df["Month"], categories=ordered_months, ordered=True)

# Create pivot table
heat_df = df.pivot(index="Department", columns="Month", values="Variance_pct")

# Build heatmap
plt.figure(figsize=(12, 6))
ax = sns.heatmap(heat_df * 100, annot=True, fmt="", cmap="coolwarm", center=0,
                 annot_kws={"fontsize": 9},
                 cbar_kws={'label': 'Variance (%)'},
                 xticklabels=True, yticklabels=True)

# Apply +/– formatting to every cell
for text in ax.texts:
    try:
        val = float(text.get_text())
        text.set_text(f"{val:+.1f}")
    except:
        pass

# Add legend below chart
legend_elements = [
    Patch(facecolor='red', edgecolor='red', label='Over Budget (+)'),
    Patch(facecolor='blue', edgecolor='blue', label='Under Budget (–)')
]
plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.15),
           ncol=2, frameon=False, title="Legend")

plt.title("Heatmap of Monthly Variance % (Jan–Dec, +/- Shown)", pad=20)
plt.tight_layout()
plt.savefig("plot3_heatmap_variance_pct_signed_legend_moved.png", dpi=300)
plt.close()

# Boxplot of Variance Distribution (Plot 4)

plt.figure(figsize=(12, 6))
ax = sns.boxplot(data=df, x="Department", y="Variance_pct", color="#2a80b9")

# Format y-axis to show percentages with +/- signs
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x * 100:+.0f}%"))

# Labels and title
plt.title("Distribution of Monthly Variance % by Department", pad=15)
plt.xlabel("Department")
plt.ylabel("Variance (%)")

# Final layout
plt.tight_layout()
plot4_boxplot_percent_path = "plot4_boxplot_variance_pct_percent.png"
plt.savefig(plot4_boxplot_percent_path, dpi=300)
plt.close()

plot4_boxplot_percent_path

# ----------------- EXECUTIVE SUMMARY & KPIs ----------------- #

# Overall KPIs
total_budget = df["Budget"].sum()
total_actual = df["Actual"].sum()
total_variance = total_actual - total_budget
total_variance_pct = total_variance / total_budget

print("\n========== FP&A Executive Summary ==========\n")
print(f"Total Budget: ${total_budget:,.0f}")
print(f"Total Actual: ${total_actual:,.0f}")
print(f"Total Variance: {total_variance:+,.0f} USD ({total_variance_pct:+.2%})\n")

# Department-level Summary
dept_summary = df.groupby("Department")[["Budget", "Actual"]].sum().reset_index()
dept_summary["Variance"] = dept_summary["Actual"] - dept_summary["Budget"]
dept_summary["Variance_pct"] = dept_summary["Variance"] / dept_summary["Budget"]

for _, row in dept_summary.iterrows():
    direction = "under" if row["Variance"] < 0 else "over"
    print(f"{row['Department']} is {abs(row['Variance_pct'])*100:.1f}% {direction} budget ({row['Variance']:+,.0f} USD)")
