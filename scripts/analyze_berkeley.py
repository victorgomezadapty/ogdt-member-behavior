"""Observe real gym behavior at the monthly grain justified in the source plan."""
from pathlib import Path
import sys
import json
import html
import base64
import hashlib
import importlib.metadata
import platform
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.berkeley import load_berkeley, monthly_observations, matlab_dates, assert_same_population, DATASET_ID, ARCHIVE_SHA256, TABLE_SHA256, POLICY_ID, KEY
from src.features.monthly import monthly_metrics, FEATURE_COLUMNS
from src.data.retention_bridge import inspect_retention_bridge


def md_table(frame):
    frame = frame.astype(object).where(frame.notna(), "—")
    def safe(v):
        return str(v).replace("|", "\\|")
    return "| " + " | ".join(frame.columns) + " |\n| " + " | ".join(["---"]*len(frame.columns)) + " |\n" + "\n".join("| " + " | ".join(map(safe,row)) + " |" for row in frame.itertuples(index=False,name=None))


def write_catalog(metrics):
    descriptions = {
        "recorded_attendance_month": ("Source attend in the eligible calendar month", "Recorded monthly attendance volume", "Current calendar month", "events"),
        "attendance_previous_month": ("Recorded count in immediately preceding eligible calendar month", "Prior comparison volume", "Previous contiguous calendar month", "events"),
        "attendance_change_vs_previous_month": ("Current count minus previous-month count", "Within-member absolute change", "Two contiguous eligible calendar months", "event_difference"),
        "attendance_pct_change_vs_previous_month": ("Current/previous-1; null if previous zero or unavailable", "Relative change with explicit denominator", "Two contiguous eligible calendar months", "fraction"),
        "attendance_sum_3_calendar_months": ("Sum of three consecutive eligible monthly counts including current", "Recent cumulative volume", "Three calendar months", "events"),
        "attendance_mean_3_calendar_months": ("Three-month sum / 3", "Nominal monthly frequency", "Three calendar months", "events_per_month"),
        "attendance_std_3_calendar_months": ("Population stddev ddof=0 over three eligible monthly counts", "Variability of recorded monthly use", "Three calendar months", "events_stddev"),
        "positive_attendance_months_3": ("Count of months with >0 recorded events in complete three-month window", "Spread of recorded use across months", "Three calendar months", "months_0_to_3"),
        "attendance_sum_6_calendar_months": ("Sum of six consecutive eligible monthly counts including current", "Longer cumulative volume", "Six calendar months", "events"),
        "attendance_mean_6_calendar_months": ("Six-month sum / 6", "Longer nominal monthly frequency", "Six calendar months", "events_per_month"),
        "consecutive_eligible_months": ("Length of current contiguous eligible observed-month run", "History support; not membership tenure", "Observed run ending in current month", "months"),
        "months_since_recorded_positive_month": ("Calendar month distance to last >0 month within current eligible run; null if none known", "Monthly recency proxy with left-edge uncertainty", "Current contiguous eligible run", "months"),
        "dataset_id": ("berkeley_gym_aer_2006", "Population namespace", "Pinned source", "identifier"),
        "member_id": ("str(int(source.id))", "Shared identity inside this source only", "Pinned source", "identifier"),
        "period_end": ("Last calendar date of source.time month after MATLAB conversion", "Monthly observation key", "Current month", "date"),
        "club_id": ("source.club: 11,13,16", "Source club context; not event-branch diversity", "Current source row", "identifier"),
        "as_of_exclusive": ("Midnight immediately following period_end", "Explicit research calculation boundary", "Month close", "datetime"),
        "synthetic": ("False", "Disclose real historical gym origin", "Pinned source", "boolean"),
        "selection_policy_id": ("berkeley_regular_month_v1", "Trace conservative row eligibility", "Current adapter version", "identifier"),
        "availability_basis": ("assumed_month_close_no_ingestion_clock", "Expose research availability assumption", "Month close", "categorical"),
        "coverage_basis": ("author_flags_and_documented_month_span", "Expose coverage/eligibility evidence basis", "Retrospective source audit", "categorical")}
    rows = []
    for field in metrics.columns:
        definition, business, window, unit = descriptions[field]
        rows.append({"feature":field,"definition":definition,"business_meaning":business,"calculation_window":window,
                     "data_requirements":"Pinned Berkeley member/month identity, attend and audited regular-month eligibility" if field in FEATURE_COLUMNS else "Pinned source identity and explicit adapter metadata",
                     "limitations":"Historical regular-month subset; no verified ingestion clock. Complete consecutive eligible windows required; missing is not zero. Not an engagement state, contractual outcome or daily metric." if field in FEATURE_COLUMNS else "Metadata/context, not an attendance state; same source identity required for joins.",
                     "unit":unit,"status":"implemented_monthly_research"})
    pd.DataFrame(rows).to_csv(ROOT / "handoff/monthly_feature_catalog.csv",index=False)


def figures(audit, features, stages, monthly, output):
    output.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    blue, teal, orange = "#235789", "#16817a", "#d06b2d"
    rendered = []
    def save(fig,name,title):
        fig.suptitle(title,x=.06,y=.98,ha="left",fontsize=16,fontweight="bold")
        fig.text(.06,.91,"REAL HISTORICAL FITNESS DATA · Berkeley · Regular-month descriptive subset",fontsize=9,color="#626b73")
        fig.text(.06,.025,"Monthly counts only. No daily visits, validated states, churn labels or causal intervention claims.",fontsize=9,color="#626b73")
        fig.tight_layout(rect=(.02,.06,.98,.86))
        fig.savefig(output / f"{name}.png",dpi=150)
        plt.close(fig)
        rendered.append((name,title))
    fig,ax=plt.subplots(figsize=(12,5))
    ax.barh(stages.stage,stages.rows,color=[blue,blue,teal,orange])
    ax.set_xlabel("Source member-month rows remaining after each sequential filter")
    ax.invert_yaxis()
    for i,row in enumerate(stages.itertuples()):
        ax.text(row.rows+3500,i,f"{row.rows:,}",va="center",fontsize=10)
    ax.set_xlim(0,stages.rows.max()*1.2)
    save(fig,"01_selection_audit","Calendar rows are filtered before describing attendance")

    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True)
    for club,g in monthly.groupby("club_id"):
        axes[0].plot(pd.to_datetime(g.period_end),g.eligible_rows,label=f"Club {club}")
        axes[1].plot(pd.to_datetime(g.period_end),g.mean_attendance,label=f"Club {club}")
    axes[0].set_ylabel("Eligible monthly observations")
    axes[1].set_ylabel("Recorded attendance / eligible month")
    axes[0].legend(ncol=3)
    axes[1].set_xlabel("Changing regular-month population; not complete gym attendance or validated seasonality")
    save(fig,"02_monthly_patterns","Monthly support and recorded attendance by source club")

    fig,axes=plt.subplots(1,2,figsize=(12,5))
    counts=features.recorded_attendance_month
    axes[0].hist(counts,bins=np.arange(-.5,counts.max()+1.5),color=blue,edgecolor="white")
    axes[0].set_xlabel("Recorded attendance per regular month")
    axes[0].set_ylabel("Eligible member-months")
    means=features.groupby(["club_id","member_id"]).recorded_attendance_month.mean().reset_index()
    groups=[g.recorded_attendance_month.to_numpy() for _,g in means.groupby("club_id")]
    axes[1].boxplot(groups,tick_labels=[str(c) for c in sorted(means.club_id.unique())],showfliers=False)
    axes[1].set_xlabel("Club; within-member mean over eligible months")
    axes[1].set_ylabel("Recorded events / eligible month")
    save(fig,"03_attendance_distributions","Monthly volume and member-level means use different weights")

    fig,axes=plt.subplots(1,2,figsize=(12,5))
    delta=features.attendance_change_vs_previous_month.dropna()
    axes[0].hist(delta,bins=np.arange(delta.min()-.5,delta.max()+1.5),color=blue,edgecolor="white")
    axes[0].axvline(0,color=orange,lw=1)
    axes[0].set_xlabel("Current − previous eligible calendar month")
    axes[0].set_ylabel("Adjacent member-month comparisons")
    support=features[FEATURE_COLUMNS].notna().sum()
    axes[1].barh(["Current month","Previous month","Full 3 months","Full 6 months","Known positive-month recency"],
                 [support.recorded_attendance_month,support.attendance_previous_month,support.attendance_sum_3_calendar_months,support.attendance_sum_6_calendar_months,support.months_since_recorded_positive_month],color=teal)
    axes[1].set_xlabel("Non-null eligible member-month rows")
    save(fig,"04_changes_and_support","Within-member changes require adjacent eligible months")

    totals=features.groupby("member_id").agg(total=("recorded_attendance_month","sum"),months=("period_end","size"))
    candidates=totals[totals.months>=6].sort_values(["total","months"],kind="stable")
    selected=candidates.iloc[[round(i*(len(candidates)-1)/5) for i in range(6)]].index
    fig,axes=plt.subplots(3,2,figsize=(12,9))
    for label,member,ax in zip("ABCDEF",selected,axes.flat):
        all_months=audit[audit.member_id.eq(member)]
        ax.plot(all_months.period_end,all_months.recorded_attendance_month,color=blue,lw=1.2,marker="o",ms=2.5)
        ax.set_ylim(-.25,max(1,all_months.recorded_attendance_month.max()*1.1))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(f"Example {label} · {int(totals.loc[member,'months'])} eligible months",fontsize=11)
        ax.set_ylabel("Monthly count")
        ax.tick_params(axis="x",rotation=30)
    save(fig,"05_individual_trajectories","Six volume-rank examples preserve unavailable-month gaps")
    return rendered


def main():
    raw=ROOT/"data/raw/berkeley/data.zip"
    out=ROOT/"data/processed/berkeley"
    reports=ROOT/"reports/berkeley"
    out.mkdir(parents=True,exist_ok=True)
    reports.mkdir(parents=True,exist_ok=True)
    source,labels=load_berkeley(raw)
    audit=monthly_observations(source)
    features=monthly_metrics(audit)
    print(f"Computed {len(features):,} regular member-months; writing local artifacts",flush=True)
    audit.to_csv(out/"member_month_eligibility.csv",index=False)
    features.to_csv(out/"member_month_metrics.csv",index=False)
    monthly=features.groupby(["club_id","period_end"]).agg(eligible_rows=("member_id","size"),members=("member_id","nunique"),
        recorded_events=("recorded_attendance_month","sum"),mean_attendance=("recorded_attendance_month","mean"),median_attendance=("recorded_attendance_month","median"),zero_fraction=("recorded_attendance_month",lambda x: x.eq(0).mean())).reset_index()
    monthly.to_csv(out/"monthly_summary.csv",index=False)
    stages=[]
    remaining=pd.Series(True,index=audit.index)
    for stage,mask in [("All source calendar rows",remaining),
                       ("Inside documented club span",~audit.excluded_outside_documented_span),
                       ("Source review flags accepted",~audit[ ["excluded_author_duplicate","excluded_author_problem","excluded_overtime"] ].any(axis=1)),
                       ("Regular contract months (1/2)",~audit.excluded_nonregular_contract)]:
        remaining=remaining & mask
        stages.append({"stage":stage,"rows":int(remaining.sum()),"members":int(audit.loc[remaining,"member_id"].nunique())})
    stages=pd.DataFrame(stages)
    stages.to_csv(out/"selection_stages.csv",index=False)
    # Verify source identity against the shared, unmodified original in Retention.
    manifest=json.loads((raw.parent/"manifest.json").read_text(encoding="utf-8"))
    shared_path=Path(manifest["copied_from"])
    shared_sha=hashlib.sha256(shared_path.read_bytes()).hexdigest() if shared_path.exists() else None
    if shared_sha != ARCHIVE_SHA256:
        raise ValueError("Cannot confirm Retention source identity; review before claiming integration")
    shared_keys=audit[KEY]
    matches=assert_same_population(features,shared_keys,TABLE_SHA256,TABLE_SHA256)
    compatibility={"dataset_id":DATASET_ID,"table_sha256":TABLE_SHA256,"local_archive_sha256":ARCHIVE_SHA256,
        "shared_retention_archive_sha256":shared_sha,"archive_identity_matches":shared_sha==ARCHIVE_SHA256,
        "source_key":["id","time"],"canonical_key":KEY,"matching_behavior_keys_in_original_population":len(matches),
        "behavior_rows":len(features),"retention_canonical_export_available":False,
        "verified_scope":"same source population and original-key compatibility; no retention target joined",
        "other_populations_joined":False}
    compatibility.update(inspect_retention_bridge(features,source,ROOT.parent/"ogdt-retention"))
    (reports/"integration_readiness.json").write_text(json.dumps(compatibility,indent=2)+"\n",encoding="utf-8")
    source_flags={name:{str(int(k)):int(v) for k,v in source[name].value_counts().sort_index().items()} for name in ["contract","duplicate","problem","overtime"]}
    months=matlab_dates(source.time)
    flag_columns=[col for col in audit if col.startswith("excluded_")]
    summary={"analysis_date":"2026-10-20","dataset_id":DATASET_ID,"synthetic":False,"source_rows":len(source),"source_members":int(source.id.nunique()),
        "source_first_month":str(months.min().date()),"source_last_month":str(months.max().date()),"eligible_rows":len(features),"eligible_members":int(features.member_id.nunique()),
        "eligible_first_period_end":str(features.period_end.min().date()),"eligible_last_period_end":str(features.period_end.max().date()),
        "recorded_events_in_eligible_rows":int(features.recorded_attendance_month.sum()),"mean_attendance_per_eligible_month":float(features.recorded_attendance_month.mean()),
        "median_attendance_per_eligible_month":float(features.recorded_attendance_month.median()),"zero_recorded_fraction":float(features.recorded_attendance_month.eq(0).mean()),
        "adjacent_comparisons":int(features.attendance_previous_month.notna().sum()),"complete_3_month_windows":int(features.attendance_sum_3_calendar_months.notna().sum()),
        "complete_6_month_windows":int(features.attendance_sum_6_calendar_months.notna().sum()),"selection_policy_id":POLICY_ID,
        "published_sample_reproduced":False,"new_model_trained":False,"contract_target_created":False,"engagement_states_validated":False}
    audit_report={"source_columns":labels,"source_missing_values":source.isna().sum().astype(int).to_dict(),"source_flag_counts":source_flags,
        "overlapping_exclusion_flag_counts":audit[flag_columns].sum().astype(int).to_dict(),"all_source_keys_preserved_in_eligibility_audit":len(audit)==len(source),
        "excluded_rows_have_null_analytic_attendance":bool(audit.loc[~audit.attendance_eligible,"recorded_attendance_month"].isna().all()),
        "feature_rows_match_eligible_rows":len(features)==int(audit.attendance_eligible.sum()),
        "historical_selection_not_point_in_time_ingestion":True}
    (reports/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (reports/"source_audit.json").write_text(json.dumps(audit_report,indent=2)+"\n",encoding="utf-8")
    environment={"python":platform.python_version(),**{p:importlib.metadata.version(p) for p in ["pandas","numpy","matplotlib","nbformat","nbclient"]}}
    (reports/"environment.json").write_text(json.dumps(environment,indent=2)+"\n",encoding="utf-8")
    write_catalog(features)
    dictionary="""# Monthly source dictionary — Berkeley

Real historical gym data. The source table has 491,506 rows and 21 variables; the labels below are taken from the inspected Stata file. No demographic values or IDs are published in this document. Read the [data readiness review](data_readiness.md) and the [monthly methodology](monthly_methodology.md) before interpreting any column.

"""
    dictionary+=md_table(pd.DataFrame([{"Field":col,"Stata label":labels[col],"Parsed type":str(source[col].dtype),"Nulls":int(source[col].isna().sum())} for col in source]))
    dictionary+="\n\nSpan limits and flags are used for review, never as predictors. `contract` belongs to selection context and to the Retention lab; it is not an automatic churn target. `time` is a month, not a visit. `birthday`, demographics and prices are not used by the adapter. Derived fields are defined in the [monthly feature catalog](../handoff/monthly_feature_catalog.csv).\n"
    (ROOT/"docs/monthly_data_dictionary.md").write_text(dictionary,encoding="utf-8")
    rendered=figures(audit,features,stages,monthly,reports/"figures")
    support=pd.DataFrame({"metric":FEATURE_COLUMNS,"non_null_rows":[int(features[c].notna().sum()) for c in FEATURE_COLUMNS]})
    delta=features.attendance_change_vs_previous_month.dropna()
    report=f"""# Real monthly behavior — Berkeley

**Gym Member Behavior & Engagement Intelligence · source review 19 October 2026; integration updated 20 October 2026**

Active research on monthly attendance with real historical gym data. The Mindweave synthetic sandbox stays separate. Suitability was reviewed before implementation: [plan](../../docs/project_plan.md), [data readiness](../../docs/data_readiness.md), [dictionary](../../docs/monthly_data_dictionary.md) and [definitions](../../docs/monthly_methodology.md).

## What the source can answer

We can describe monthly volume, change and consistency for the same population used by the Retention lab. The public table has no individual visits: it does not support days since the last visit, time of day, weekday, or exact 7/30/90-day windows. Provenance is the [author archive](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml); names and flags were checked against the Stata file, README and code in the ZIP. Months and metrics come from 1997–2001, not from a present-day gym.

## Population and selection before analysis

Source: **{len(source):,} rows**, **{source.id.nunique():,} IDs** and **21 variables**. The key `(id,time)` is unique. Main subset: **{len(features):,} regular months from {features.member_id.nunique():,} members**, under policy `{POLICY_ID}`. These counts do not reproduce the published 7,752-member sample or all of its exclusions.

{md_table(stages)}

The cascade applies filters in sequence; individual flags can overlap. It requires regular contracts 1/2, accepted flags and the documented period. Months without a contract, prorated, frozen, promotional, ambiguous or outside follow-up are excluded from the main analysis. The eligibility table keeps every original key and sets the analytical attendance of excluded months to null. **Excluded months are never imputed as zero.**

Club 11 has attendance in August 2000, but every row for that month has overtime=1 and is excluded. The main period therefore ends in July 2000 for that club and in February 2001 for the other two. Coverage is never decided from the mere presence of rows or positive counts.

After all filters are combined, eligible rows run from **{summary['eligible_first_period_end']}** to **{summary['eligible_last_period_end']}**. Published limits do not guarantee that every boundary month contributes eligible rows under this policy.

## Recorded attendance in eligible months

The selected months contain **{summary['recorded_events_in_eligible_rows']:,} recorded visits**: mean **{summary['mean_attendance_per_eligible_month']:.2f}**, median **{summary['median_attendance_per_eligible_month']:.1f}**, and **{summary['zero_recorded_fraction']:.1%} of months with zero recorded**. The denominator is eligible member-months, not all members or all gym attendance. These zeros are kept; they are not Dormant or churn labels. The regular-month composition varies by club and month, and the chart does not validate seasonality or causal effects.

## Monthly trajectories and windows

There are **{summary['adjacent_comparisons']:,} comparisons of adjacent eligible months**, **{summary['complete_3_month_windows']:,} complete three-month windows** and **{summary['complete_6_month_windows']:,} six-month windows**. Gaps and exclusions break every run; separated months are never compared as if they were consecutive.

Among valid comparisons: **{int(delta.gt(0).sum()):,} positive differences**, **{int(delta.eq(0).sum()):,} equal** and **{int(delta.lt(0).sum()):,} negative**. These are arithmetic signs, not validated states. The percentage change is null when the previous month is zero. Run length is not called contract tenure, and distance to the last positive month is not turned into daily recency.

{md_table(support)}

The six volume trajectories A–F keep nulls and breaks in excluded months; they are not segments or a probability sample. Monthly aggregation cannot reconstruct day or hour habits. A zero standard deviation across zero-attendance months does not demonstrate a stable habit either.

## Compatibility with Retention

The frozen ZIP is byte-identical to Retention's local source: `{ARCHIVE_SHA256}`. Stata table: `{TABLE_SHA256}`. All **{len(matches):,} metric keys** match the shared original population using `(dataset_id, member_id, period_end)` with `dataset_id={DATASET_ID}`.

The final check reflects the current state of Retention. Canonical export available: **{compatibility['retention_canonical_export_available']}**. Canonical rows matched: **{compatibility.get('matched_canonical_rows',0):,}**; rows only in Member Behavior: **{compatibility.get('behavior_only_rows',0):,}**. When the export exists, current counts and month boundaries are checked for equality. Population differences are explained by family observed to date, which Retention excludes; our windows are also stricter and do not include its earlier prorated months. Feature names and transformations are not interchangeable for its model.

Retention already has its own target **{compatibility.get('retention_existing_target_version','not inspected')}** and a historical benchmark in its module, according to the inspected contract. **No outcomes or scores are imported here**, that model is not retrained and no operational use is promoted. If the export is unavailable, verification is limited to source and original keys, as the JSON records. [Updated compatibility evidence](integration_readiness.json).

Berkeley members are never linked with Mindweave or Lisbon. The verification code rejects different namespaces or hashes even when IDs look alike. No Retention file was changed. [Integration evidence](integration_readiness.json).

## Limits and next step

The design describes regular months of a historical sample; it does not fully reproduce the paper's filters or validate behavior in present-day gyms. Flags and follow-up ends shape a retrospective selection. They are not predictors, and the archive has no ingestion clock. For research, the aggregate is assumed to be available at month close; this is not demonstrated for production.

Retention's own target is restricted to recorded discontinuity between clear states and keeps other outcomes unknown; it is not permanent churn or present-day gym scoring. Code 7 is not turned into churn here. No model was trained in this lab, and no engagement states, clusters or risk were assigned. Redistribution terms must be resolved before original rows or identifiable derivatives are published. Person-level files stay local and are ignored by Git.

The next viable step is to review core admission and the selection/history policy across consumers, keeping behavior features and future outcomes separate. Retention's existing benchmark keeps its own limits and target definition. This feature comparison does not demonstrate intervention effects or validate engagement states. No daily detail needs to be invented, and no clustering is needed to complete this descriptive phase.

## Reproduce

`python scripts/acquire_berkeley.py --download` (or `--source ../ogdt-retention/data/raw/berkeley/data.zip`), then `python scripts/analyze_berkeley.py`, `python scripts/execute_notebooks.py --notebook 07_berkeley_monthly_eda.ipynb` and `python scripts/verify_berkeley.py`. See the [monthly contract](../../handoff/monthly_data_contract.yaml) and [catalog](../../handoff/monthly_feature_catalog.csv). Source review and processing do not alter the target or the Retention lab.

## Figures

"""
    for name,title in rendered:
        if "individual_trajectories" in name:
            # Per-person derivative: kept in the local report only, never published.
            report+=f"### {title}\n\n*Kept local only.* This figure shows six individual members' monthly series. Redistribution rights for the source are not established, so it is excluded from Git and every public output.\n\n"
        else:
            report+=f"### {title}\n\n![{title}](figures/{name}.png)\n\n"
    (reports/"report.md").write_text(report,encoding="utf-8")
    gallery="".join(f'<section><h2>{html.escape(title)}</h2><img alt="{html.escape(title)}" src="data:image/png;base64,{base64.b64encode((reports/f"figures/{name}.png").read_bytes()).decode()}"></section>' for name,title in rendered)
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OGDT · Berkeley monthly behavior</title><style>body{{font:16px/1.65 system-ui;background:#f1f4f7;color:#172a3a;margin:0}}main{{max-width:1100px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(30px,5vw,48px);line-height:1.15}}.note{{padding:20px;background:#e1efeb;border-left:5px solid #16817a}}section{{padding:20px;background:white;margin:24px 0;border-radius:10px}}img{{width:100%;height:auto}}pre{{white-space:pre-wrap;font:14px/1.65 system-ui}}a{{color:#235789}}</style><main><p>OPEN GYM DIGITAL TWIN / MEMBER BEHAVIOR</p><h1>Monthly attendance.<br>A real fitness population.</h1><p>20 October 2026 · Berkeley · {len(features):,} regular months · {features.member_id.nunique():,} members</p><div class="note"><strong>Real historical data, with documented selection and coverage.</strong><br>The evidence is monthly. No daily visits are reconstructed and no validated states or churn probabilities are assigned. The synthetic sandbox is kept separate. This local report includes one per-person figure; it is never published.</div><p><a href="report.md">Full report</a> · <a href="../../docs/project_plan.md">Plan and suitability</a> · <a href="../../handoff/monthly_data_contract.yaml">Monthly contract</a> · <a href="integration_readiness.json">Shared identity with Retention</a></p>{gallery}<section><h2>Results, limits and definitions</h2><pre>{html.escape(report.split('## Figures')[0])}</pre></section></main></html>'''
    (reports/"report.html").write_text(page,encoding="utf-8")
    cells=[nbf.v4.new_markdown_cell("# 07 · Real monthly behavior — Berkeley\n\nThe source was reviewed before implementation; see docs/project_plan.md and docs/data_readiness.md. This is a descriptive subset of regular months and does not reproduce the paper's full sample. No daily visits, targets or validated states are created. Retention's final contract already has its own target and benchmark; here only features, keys and boundaries are compared."),
        nbf.v4.new_code_cell('from pathlib import Path\nimport sys,json\nimport pandas as pd\nfrom IPython.display import display,Image\nROOT=Path.cwd()\nif not (ROOT/"src").is_dir(): ROOT=ROOT.parent\nsys.path.insert(0,str(ROOT))\nfrom src.data.berkeley import load_berkeley,monthly_observations\nfrom src.features.monthly import monthly_metrics\nsource,labels=load_berkeley(ROOT/"data/raw/berkeley/data.zip")\naudit=monthly_observations(source)\nfeatures=monthly_metrics(audit)\nprint("Real source:",len(source),"rows;",source.id.nunique(),"IDs")\nprint("Regular months:",len(features),"from",features.member_id.nunique(),"members")\nassert not features.synthetic.any()\nassert audit.loc[~audit.attendance_eligible,"recorded_attendance_month"].isna().all()'),
        nbf.v4.new_code_cell('display(pd.read_csv(ROOT/"data/processed/berkeley/selection_stages.csv"))\ndisplay(pd.read_csv(ROOT/"handoff/monthly_feature_catalog.csv"))\ndisplay(features.drop(columns="member_id").describe().T)\nprint((ROOT/"reports/berkeley/integration_readiness.json").read_text(encoding="utf-8"))'),
        # Individual trajectories stay in the local report only: they are per-person derivatives and
        # redistribution rights for the source are not established.
        nbf.v4.new_code_cell('for path in sorted((ROOT/"reports/berkeley/figures").glob("*.png")):\n    if "individual_trajectories" not in path.name:\n        display(Image(filename=str(path)))'),
        nbf.v4.new_markdown_cell("## Interpretation\n\nWindows require consecutive eligible months. Gaps are not zeros. Runs and monthly recency are not tenure or daily recency. The Retention comparison checks its actual feature export and explains selection/history differences; its outcomes and scores are not imported and its model features are not replaced. No other populations are joined. Availability at month close is an assumption without an ingestion clock; results are historical and descriptive.")]
    nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"name":"python3","display_name":"Python 3","language":"python"},"ogdt":{"synthetic":False,"scope":"berkeley_monthly_observe"}})
    nbf.write(nb,ROOT/"notebooks/07_berkeley_monthly_eda.ipynb")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
