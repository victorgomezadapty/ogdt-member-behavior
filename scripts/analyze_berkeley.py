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
    dictionary="""# Diccionario de origen mensual — Berkeley

Datos históricos reales de gimnasio. El archivo de origen contiene 491.506 filas y 21 variables; las etiquetas siguientes se extraen del Stata inspeccionado. No se publican valores demográficos ni IDs en este documento. Ver [adecuación](data_readiness.md) y [metodología](monthly_methodology.md) antes de interpretar columnas.

"""
    dictionary+=md_table(pd.DataFrame([{"Field":col,"Stata label":labels[col],"Parsed type":str(source[col].dtype),"Nulls":int(source[col].isna().sum())} for col in source]))
    dictionary+="\n\nLos límites y flags se usan para revisión, no como predictores. `contract` pertenece al contexto de selección y al trabajo de Retention; no es un target de churn automático. `time` representa un mes, no una visita. `birthday`, demografía y precios no se utilizan en el adaptador. Las definiciones de los campos derivados están en el [catálogo mensual](../handoff/monthly_feature_catalog.csv).\n"
    (ROOT/"docs/monthly_data_dictionary.md").write_text(dictionary,encoding="utf-8")
    rendered=figures(audit,features,stages,monthly,reports/"figures")
    support=pd.DataFrame({"metric":FEATURE_COLUMNS,"non_null_rows":[int(features[c].notna().sum()) for c in FEATURE_COLUMNS]})
    delta=features.attendance_change_vs_previous_month.dropna()
    report=f"""# Comportamiento mensual real — Berkeley

**Gym Member Behavior & Engagement Intelligence · revisión de fuente 19 de octubre; integración actualizada 20 de octubre de 2026**

Investigación activa de asistencia mensual con datos históricos reales de gimnasio. El sandbox sintético Mindweave permanece separado. Se revisó la adecuación antes de implementar: [plan](../../docs/project_plan.md), [evaluación](../../docs/data_readiness.md), [diccionario](../../docs/monthly_data_dictionary.md) y [definiciones](../../docs/monthly_methodology.md).

## Qué permite responder la fuente

Podemos describir volumen, cambios y consistencia mensual para la misma población que usa Retention. No contiene visitas individuales públicas en esta tabla: no permite días desde la última visita, horarios, días de semana ni ventanas exactas de 7/30/90 días. La procedencia es el [archivo del autor](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml); los nombres y flags se verificaron en el Stata, README y código del ZIP. Las fechas mensuales y las métricas son de 1997–2001, no de un gimnasio actual.

## Población y selección antes de analizar

Origen: **{len(source):,} filas**, **{source.id.nunique():,} IDs** y **21 variables**. Clave `(id,time)` única. Subconjunto principal: **{len(features):,} meses regulares de {features.member_id.nunique():,} miembros**, bajo política `{POLICY_ID}`. Estos conteos no reproducen la muestra publicada de 7.752 miembros ni sus exclusiones completas.

{md_table(stages)}

La cascada aplica filtros secuenciales; los flags individuales pueden solaparse. Exige contratos regulares 1/2, flags aceptados y periodo documentado. Los meses sin contrato, prorrateados, congelados, promocionales, ambiguos y fuera de seguimiento se excluyen del análisis principal. La tabla de elegibilidad conserva todas las claves originales y convierte su asistencia analítica a nulo. **No se imputan ceros a meses excluidos.**

El club 1 tiene asistencias en agosto de 2000, pero todas sus filas de ese mes tienen overtime=1 y quedan fuera. El periodo principal termina en julio de 2000 para ese club y en febrero de 2001 para los otros dos. No se decide cobertura mirando únicamente la existencia de filas o de conteos positivos.

Después de combinar todos los filtros, las filas elegibles efectivas van de **{summary['eligible_first_period_end']}** a **{summary['eligible_last_period_end']}**. Los límites publicados no garantizan que cada mes de frontera aporte filas elegibles bajo esta política.

## Asistencia registrada en meses elegibles

Se contabilizan **{summary['recorded_events_in_eligible_rows']:,} asistencias** dentro de los meses seleccionados, media **{summary['mean_attendance_per_eligible_month']:.2f}**, mediana **{summary['median_attendance_per_eligible_month']:.1f}** y **{summary['zero_recorded_fraction']:.1%} de meses con cero registrado**. El denominador es meses-persona elegibles, no todos los socios o toda la asistencia del gimnasio. Estos ceros se preservan; no son etiquetas Dormant o churn. La composición regular varía por club/mes y la gráfica no valida estacionalidad ni efectos causales.

## Trayectorias y ventanas mensuales

Hay **{summary['adjacent_comparisons']:,} comparaciones de meses adyacentes elegibles**, **{summary['complete_3_month_windows']:,} ventanas completas de tres meses** y **{summary['complete_6_month_windows']:,} de seis meses**. Los huecos o exclusiones interrumpen cada racha; no se comparan meses separados como si fueran consecutivos.

Entre las comparaciones válidas: **{int(delta.gt(0).sum()):,} diferencias positivas**, **{int(delta.eq(0).sum()):,} iguales** y **{int(delta.lt(0).sum()):,} negativas**. Son signos aritméticos, no estados validados. El porcentaje de cambio es nulo con denominador previo cero. La longitud de racha no se denomina antigüedad contractual, y la distancia al último mes positivo no se convierte en recencia diaria.

{md_table(support)}

Las seis trayectorias de volumen A–F conservan nulos/cortes en meses excluidos; no representan segmentos ni una muestra probabilística. La agregación mensual no permite reconstruir hábitos por día/hora. Una desviación estándar cero en meses con cero asistencia tampoco acredita hábito estable.

## Compatibilidad con Retention

El ZIP congelado coincide byte a byte con el origen local de Retention: `{ARCHIVE_SHA256}`. Tabla Stata: `{TABLE_SHA256}`. Las **{len(matches):,} claves** de métricas encuentran correspondencia en la población original compartida, usando `(dataset_id, member_id, period_end)` con `dataset_id={DATASET_ID}`.

La inspección final se actualiza con el estado vigente de Retention. Export canónico disponible: **{compatibility['retention_canonical_export_available']}**. Filas canónicas cotejadas: **{compatibility.get('matched_canonical_rows',0):,}**; filas exclusivas de Member Behavior: **{compatibility.get('behavior_only_rows',0):,}**. Cuando existe el export, se verifican igualdad del conteo actual y equivalencia de frontera mensual. Las diferencias de población se explican mediante familia observada hasta ese mes, excluida por Retention; nuestras ventanas también son más estrictas y no incluyen sus meses prorrateados previos. Los nombres/transformaciones de features no son intercambiables para su modelo.

Retention ya dispone del target propio **{compatibility.get('retention_existing_target_version','no inspeccionado')}** y de un benchmark histórico en su módulo, según el contrato inspeccionado. Aquí **no se importan outcomes ni scores**, no se reentrena ese modelo y no se promueve uso operativo. Si el export no está disponible, la verificación queda limitada a origen y claves originales, como indica el JSON. [Evidencia actualizada de compatibilidad](integration_readiness.json).

No se cruzan personas de Berkeley con Mindweave ni Lisboa. El código de verificación rechaza namespaces o hashes distintos aunque los IDs se parezcan. No se cambió ningún archivo de Retention. [Evidencia de integración](integration_readiness.json).

## Limitaciones y próximo paso

El diseño describe meses regulares de una muestra histórica; no reproduce por completo los filtros del artículo ni valida comportamiento de gimnasios actuales. Flags y fines de seguimiento condicionan selección retrospectiva. No son predictores; el archivo tampoco contiene reloj de ingesta. Se asume que el agregado está disponible al cierre del mes para investigación, sin acreditarlo en producción.

El target propio de Retention se restringe a discontinuidad registrada entre estados claros y mantiene otros resultados desconocidos; no equivale a churn permanente ni a scoring actual de un gimnasio. El código 7 no se convierte aquí en churn. No se entrenó un modelo en este laboratorio ni se asignaron estados de engagement, clusters o riesgo. Antes de publicar filas originales/derivados identificables se deben resolver términos de redistribución. Los archivos por persona quedan solo locales e ignorados por Git.

El siguiente paso viable es revisar la admisión en core y la política de selección/historial entre consumidores, manteniendo separados features de conducta y resultados futuros. El benchmark ya existente de Retention conserva sus propios límites y definición de target. Este cotejo de features no acredita efectos de intervención ni valida estados de engagement. No se necesita inventar detalle diario ni añadir clustering para completar esta fase descriptiva.

## Reproducir

`python scripts/acquire_berkeley.py --source ../ogdt-retention/data/raw/berkeley/data.zip`, después `python scripts/analyze_berkeley.py`, `python scripts/execute_notebooks.py --notebook 07_berkeley_monthly_eda.ipynb` y `python scripts/verify_berkeley.py`. Ver [contrato mensual](../../handoff/monthly_data_contract.yaml) y [catálogo](../../handoff/monthly_feature_catalog.csv). La revisión de fuente y el procesamiento no alteran el target ni el laboratorio Retention.

## Figuras

"""
    for name,title in rendered:
        report+=f"### {title}\n\n![{title}](figures/{name}.png)\n\n"
    (reports/"report.md").write_text(report,encoding="utf-8")
    gallery="".join(f'<section><h2>{html.escape(title)}</h2><img alt="{html.escape(title)}" src="data:image/png;base64,{base64.b64encode((reports/f"figures/{name}.png").read_bytes()).decode()}"></section>' for name,title in rendered)
    page=f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OGDT · Comportamiento mensual Berkeley</title><style>body{{font:16px/1.65 system-ui;background:#f1f4f7;color:#172a3a;margin:0}}main{{max-width:1100px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(30px,5vw,48px);line-height:1.15}}.note{{padding:20px;background:#e1efeb;border-left:5px solid #16817a}}section{{padding:20px;background:white;margin:24px 0;border-radius:10px}}img{{width:100%;height:auto}}pre{{white-space:pre-wrap;font:14px/1.65 system-ui}}a{{color:#235789}}</style><main><p>OPEN GYM DIGITAL TWIN / MEMBER BEHAVIOR</p><h1>Asistencia mensual.<br>Una población fitness real.</h1><p>19 de octubre de 2026 · Berkeley · {len(features):,} meses regulares · {features.member_id.nunique():,} miembros</p><div class="note"><strong>Datos reales históricos, con selección y cobertura documentadas.</strong><br>La evidencia es mensual. No se reconstruyen visitas diarias ni se asignan estados validados o probabilidades de churn. El sandbox sintético se conserva separado.</div><p><a href="report.md">Informe completo</a> · <a href="../../docs/project_plan.md">Plan y adecuación</a> · <a href="../../handoff/monthly_data_contract.yaml">Contrato mensual</a> · <a href="integration_readiness.json">Identidad compartida con Retention</a></p>{gallery}<section><h2>Resultados, límites y definiciones</h2><pre>{html.escape(report.split('## Figuras')[0])}</pre></section></main></html>'''
    page=page.replace("19 de octubre de 2026 · Berkeley", "20 de octubre de 2026 · Berkeley")
    (reports/"report.html").write_text(page,encoding="utf-8")
    cells=[nbf.v4.new_markdown_cell("# 07 · Comportamiento mensual real — Berkeley\n\nLa fuente fue revisada antes de implementar. Ver docs/project_plan.md y docs/data_readiness.md. Subconjunto descriptivo de meses regulares; no reproduce toda la muestra del artículo. No se crean visitas diarias, targets o estados validados. El contrato final de Retention ya dispone de un target y benchmark propios; aquí solo se cotejan features, claves y fronteras."),
        nbf.v4.new_code_cell('from pathlib import Path\nimport sys,json\nimport pandas as pd\nfrom IPython.display import display,Image\nROOT=Path.cwd()\nif not (ROOT/"src").is_dir(): ROOT=ROOT.parent\nsys.path.insert(0,str(ROOT))\nfrom src.data.berkeley import load_berkeley,monthly_observations\nfrom src.features.monthly import monthly_metrics\nsource,labels=load_berkeley(ROOT/"data/raw/berkeley/data.zip")\naudit=monthly_observations(source)\nfeatures=monthly_metrics(audit)\nprint("Origen real:",len(source),"filas;",source.id.nunique(),"IDs")\nprint("Meses regulares:",len(features),"de",features.member_id.nunique(),"miembros")\nassert not features.synthetic.any()\nassert audit.loc[~audit.attendance_eligible,"recorded_attendance_month"].isna().all()'),
        nbf.v4.new_code_cell('display(pd.read_csv(ROOT/"data/processed/berkeley/selection_stages.csv"))\ndisplay(pd.read_csv(ROOT/"handoff/monthly_feature_catalog.csv"))\ndisplay(features.drop(columns="member_id").describe().T)\nprint((ROOT/"reports/berkeley/integration_readiness.json").read_text(encoding="utf-8"))'),
        nbf.v4.new_code_cell('for path in sorted((ROOT/"reports/berkeley/figures").glob("*.png")):\n    display(Image(filename=str(path)))'),
        nbf.v4.new_markdown_cell("## Interpretación\n\nLas ventanas requieren meses consecutivos elegibles. Los huecos no son ceros. Rachas y recencia mensual no son antigüedad ni recencia diaria. La compatibilidad con Retention coteja su export real de features y explica diferencias de selección/historial; no se importan sus outcomes ni scores y no se reemplazan features de su modelo. No se unen otras poblaciones. La disponibilidad al cierre mensual es una hipótesis sin reloj de ingesta; los resultados son históricos y descriptivos.")]
    nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"name":"python3","display_name":"Python 3","language":"python"},"ogdt":{"synthetic":False,"scope":"berkeley_monthly_observe"}})
    nbf.write(nb,ROOT/"notebooks/07_berkeley_monthly_eda.ipynb")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
