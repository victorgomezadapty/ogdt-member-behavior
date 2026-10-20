from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BLUE, TEAL, ORANGE = "#235789", "#16817a", "#d06b2d"


def create_figures(tables, joined, monthly, weekly, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "figure.facecolor": "white"})
    c, m = tables["checkins"], tables["members"]
    figures = []

    def save(fig, name, title):
        fig.suptitle(title, fontsize=16, fontweight="bold", x=.06, y=.985, ha="left")
        fig.text(.06, .91, "SYNTHETIC PUBLIC SAMPLE | 300 roster members; only 32 with exported visits", color="#626b73", fontsize=9)
        fig.text(.06, .025, "Zero exported events do not establish inactivity. Coverage and timezone are unverified.", fontsize=9, color="#626b73")
        fig.tight_layout(rect=(.02, .06, .98, .86))
        fig.savefig(output / f"{name}.png", dpi=160)
        plt.close(fig)
        figures.append((name, title))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(["Roster", "With exported visits", "No exported visits"], [len(m), c.member_id.nunique(), len(m)-c.member_id.nunique()], color=[BLUE, TEAL, ORANGE])
    axes[0].set_ylabel("Members")
    counts = c.groupby("member_id").size()
    axes[1].hist(counts, bins=12, color=BLUE, edgecolor="white")
    axes[1].set_xlabel("Exported events / member across observation span")
    axes[1].set_ylabel("Members with at least one event")
    save(fig, "01_coverage_and_volume", "Coverage comes before engagement interpretation")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    daily = c.groupby(c.checkin_datetime.dt.normalize()).size().reindex(pd.date_range(c.checkin_datetime.min().normalize(), c.checkin_datetime.max().normalize()), fill_value=0)
    axes[0].plot(daily.index, daily, color=BLUE, linewidth=.8, alpha=.5, label="Daily exported events")
    axes[0].plot(daily.index, daily.rolling(28, min_periods=28).mean(), color=ORANGE, label="28-day trailing mean")
    axes[0].set_ylabel("Events / calendar day")
    axes[0].legend(loc="upper left")
    axes[1].plot(pd.to_datetime(monthly.month), monthly.exported_events, marker="o", color=TEAL)
    axes[1].set_ylabel("Events / month")
    axes[1].set_xlabel("First and last observed months are boundary months; completeness unknown")
    save(fig, "02_visit_timeline", "Visit timeline: observed export, January 2023–December 2024")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(weekly.exported_events, bins=range(0, int(weekly.exported_events.max())+2), color=BLUE, edgecolor="white")
    axes[0].set_xlabel("Exported events / member / calendar week")
    axes[0].set_ylabel("Member-weeks in selected 32-member panel")
    axes[1].hist(monthly.attrs["member_panel"].exported_events, bins=15, color=TEAL, edgecolor="white")
    axes[1].set_xlabel("Exported events / member / calendar month")
    axes[1].set_ylabel("Member-months in selected 32-member panel")
    save(fig, "03_week_month_distributions", "Volume distributions include zero-export periods after signup")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    day_counts = c.checkin_datetime.dt.dayofweek.value_counts().reindex(range(7), fill_value=0)
    calendar = pd.date_range(c.checkin_datetime.min().normalize(), c.checkin_datetime.max().normalize())
    day_exposure = pd.Series(calendar.dayofweek).value_counts().reindex(range(7))
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    axes[0].bar(labels, day_counts, color=BLUE)
    axes[0].set_ylabel("Exported events")
    axes[1].bar(labels, day_counts / day_exposure, color=TEAL)
    axes[1].set_ylabel("Exported events / observed calendar day")
    save(fig, "04_day_preference", "Day of week: raw counts and calendar-day adjustment")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    hours = c.checkin_datetime.dt.hour.value_counts().reindex(range(24), fill_value=0)
    axes[0].bar(hours.index, hours, color=BLUE)
    axes[0].set_xticks(range(0, 24, 3))
    axes[0].set_xlabel("Recorded clock hour (timezone unspecified)")
    axes[0].set_ylabel("Exported events")
    slots = joined.time_band.value_counts().reindex(["00–04", "05–11", "12–16", "17–21", "22–23"], fill_value=0)
    axes[1].bar(slots.index.astype(str), slots, color=TEAL)
    axes[1].set_xlabel("Display bins only; unequal lengths")
    axes[1].set_ylabel("Exported events")
    save(fig, "05_time_preference", "Time of day: preserve the source clock")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    tenure = joined.groupby("tenure_band", observed=False).agg(events=("id", "size"), members=("member_id", "nunique"))
    axes[0].bar(tenure.index.astype(str), tenure.events, color=BLUE)
    axes[0].set_ylabel("Exported events")
    axes[0].tick_params(axis="x", labelrotation=20)
    axes[0].set_xlabel("Days since signup at visit; counts are not exposure-adjusted")
    axes[1].bar(tenure.index.astype(str), tenure.members, color=TEAL)
    axes[1].set_ylabel("Distinct members contributing events")
    axes[1].tick_params(axis="x", labelrotation=20)
    save(fig, "06_membership_tenure", "Tenure describes event age, with unequal follow-up")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    branch = joined.groupby("visit_branch").agg(events=("id", "size"), members=("member_id", "nunique"))
    axes[0].barh(branch.index, branch.events, color=BLUE)
    axes[0].set_xlabel("Exported events")
    plan = joined.groupby("plan_name").agg(events=("id", "size"), members=("member_id", "nunique"))
    axes[1].barh(plan.index, plan.events, color=TEAL)
    axes[1].set_xlabel("Exported events; static plan snapshot")
    save(fig, "07_branch_and_plan", "Branch and plan comparisons reflect selected members")

    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    season = monthly.copy()
    season["year"] = pd.to_datetime(season.month).dt.year
    season["month_number"] = pd.to_datetime(season.month).dt.month
    for year, subset in season.groupby("year"):
        axes[0].plot(subset.month_number, subset.exported_events, marker="o", label=str(year))
    axes[0].set_xticks(range(1, 13))
    axes[0].set_ylabel("Exported events")
    axes[0].legend()
    signups = m.groupby(m.signup_date.dt.to_period("M")).size()
    axes[1].bar(signups.index.astype(str), signups, color=TEAL)
    axes[1].tick_params(axis="x", labelrotation=65)
    axes[1].set_ylabel("Signups in 300-member roster")
    axes[1].set_xlabel("Calendar patterns are descriptive; two synthetic years cannot validate seasonality")
    save(fig, "08_monthly_patterns", "Month-of-year attendance and signup patterns")

    panel = monthly.attrs["member_panel"]
    pivot = panel.pivot(index="member_id", columns="month", values="exported_events")
    fig, ax = plt.subplots(figsize=(12, 8))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", interpolation="nearest", cmap="YlGnBu")
    ax.set_yticks(range(len(pivot)), pivot.index)
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=65, ha="right")
    ax.set_ylabel("Member ID; white = before signup / no calendar exposure")
    fig.colorbar(image, ax=ax, label="Exported events / calendar month")
    save(fig, "09_member_month_heatmap", "Individual histories: 32 members with at least one exported visit")

    ranked = counts.sort_values()
    # Evenly spaced ranks, deterministic; not selected to imply desired states.
    positions = sorted(set(round(i * (len(ranked)-1) / 5) for i in range(6)))
    selected = ranked.iloc[positions].index.tolist()
    fig, axes = plt.subplots(3, 2, figsize=(12, 9), sharex=True)
    for ax, member_id in zip(axes.flat, selected):
        trajectory = panel[panel.member_id == member_id]
        month_ends = pd.to_datetime(trajectory.month) + pd.offsets.MonthEnd(0)
        month_ends = month_ends.clip(upper=c.checkin_datetime.max().normalize())
        ax.plot(month_ends, trajectory.exported_events, color=BLUE, marker="o", ms=3)
        ax.set_ylim(bottom=0)
        signup = m.loc[m.id == member_id, "signup_date"].iloc[0]
        ax.axvline(signup, color=TEAL, ls=":", label="Signup")
        # Contract dates are descriptive overlays; no labels or risk prediction.
        cancellation = m.loc[m.id == member_id, "cancel_date"].iloc[0]
        if pd.notna(cancellation):
            ax.axvline(cancellation, color=ORANGE, ls="--", label="Recorded cancellation")
        ax.set_title(f"Member {member_id} | {counts.loc[member_id]} total exported events", fontsize=10)
        ax.set_ylabel("Events / month")
        ax.legend(fontsize=7)
        ax.tick_params(axis="x", labelrotation=30)
    save(fig, "10_individual_trajectories", "Six trajectories: monthly totals anchored at period end")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    first30 = joined[joined.tenure_days < 30].groupby("member_id").size()
    cohort = m[m.id.isin(c.member_id) & (m.signup_date >= c.checkin_datetime.min().normalize()) &
               (m.signup_date + pd.Timedelta(days=30) <= c.checkin_datetime.max().normalize() + pd.Timedelta(days=1))]
    early = first30.reindex(cohort.id, fill_value=0)
    axes[0].hist(early, bins=12, color=BLUE, edgecolor="white")
    axes[0].set_xlabel(f"Exported events in first 30 tenure days (n={len(cohort)})")
    axes[0].set_ylabel("Selected members with calendar opportunity")
    gaps = c.sort_values("checkin_datetime").groupby("member_id").checkin_datetime.diff().dt.total_seconds().div(86400).dropna()
    axes[1].hist(gaps, bins=30, color=TEAL, edgecolor="white")
    axes[1].set_xlabel("Days between consecutive exported events")
    axes[1].set_ylabel("Intervals; includes same-day repeat visits")
    save(fig, "11_early_behavior_and_gaps", "Early attendance and gaps remain sample-dependent")
    return figures
