import inspect

import koreanize_matplotlib  # noqa: F401  matplotlib 한글 폰트(NanumGothic) 자동 설정
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="시각화 라이브러리 비교", page_icon="🎨", layout="wide")

# -----------------------------------------------------------------------------
# 색상 팔레트 (계열 색상은 항목에 고정 — 순서대로 배정)

PINK, BLUE, AMBER, TEAL = "#FF3D8B", "#3D5AFE", "#FFA000", "#00A98F"
INK, MUTED, GRID = "#1E1B3A", "#6B6887", "#ECE8F5"

MENU_COLORS = {"아메리카노": BLUE, "카페라떼": PINK, "레몬에이드": AMBER, "딸기스무디": TEAL}
MENU_MARKERS = {"아메리카노": "o", "카페라떼": "s", "레몬에이드": "^", "딸기스무디": "D"}
CLASS_COLORS = {"1반": PINK, "2반": BLUE, "3반": AMBER}
CLASS_MARKERS = {"1반": "o", "2반": "s", "3반": "^"}

FIG_SIZE = (6.4, 4.4)
# seaborn 스타일이 한글 폰트를 덮어쓰지 않도록 폰트를 함께 지정
SNS_STYLE = {"grid.color": GRID, "axes.edgecolor": "#C9C4DA", "font.family": "NanumGothic"}

# -----------------------------------------------------------------------------
# 예시 데이터


@st.cache_data
def make_cafe_sales():
    """카페 메뉴별 월간 판매량 (12개월 × 4개 메뉴)"""
    rng = np.random.default_rng(7)
    months = np.arange(1, 13)
    summer = np.sin((months - 4) / 12 * 2 * np.pi)  # 7월 전후 최고
    base = {
        "아메리카노": 820 - 60 * summer,
        "카페라떼": 560 - 140 * summer,
        "레몬에이드": 390 + 260 * summer,
        "딸기스무디": 300 + 120 * np.cos((months - 3) / 12 * 2 * np.pi),
    }
    rows = [
        {"월": m, "메뉴": menu, "판매량": int(v + rng.normal(0, 25))}
        for menu, values in base.items()
        for m, v in zip(months, values)
    ]
    return pd.DataFrame(rows)


@st.cache_data
def make_study_scores():
    """학생별 주간 공부 시간과 시험 점수 (3개 반 × 40명)"""
    rng = np.random.default_rng(42)
    rows = []
    for cls, (hour_mean, bonus) in {"1반": (9, 4), "2반": (12, 0), "3반": (7, 8)}.items():
        hours = np.clip(rng.normal(hour_mean, 3.2, 40), 1, 20)
        scores = np.clip(38 + 3.1 * hours + bonus + rng.normal(0, 7, 40), 0, 100)
        rows += [
            {"반": cls, "공부 시간": round(h, 1), "시험 점수": round(s)}
            for h, s in zip(hours, scores)
        ]
    return pd.DataFrame(rows)


cafe_df = make_cafe_sales()
study_df = make_study_scores()

# -----------------------------------------------------------------------------
# 차트: 데이터 1 — 월별 판매량 (선 그래프)


def cafe_matplotlib(df):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for menu, color in MENU_COLORS.items():
        d = df[df["메뉴"] == menu]
        ax.plot(d["월"], d["판매량"], color=color, lw=2, marker=MENU_MARKERS[menu],
                ms=6, mec="white", mew=1.5, label=menu)
    ax.set_title("메뉴별 월간 판매량", fontsize=14, fontweight="bold", color=INK, loc="left")
    ax.set_xlabel("월", color=MUTED)
    ax.set_ylabel("판매량 (잔)", color=MUTED)
    ax.set_xticks(range(1, 13), [f"{m}월" for m in range(1, 13)])
    ax.grid(axis="y", color=GRID)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C9C4DA")
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(title="메뉴", frameon=False, fontsize=9, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    return fig


def cafe_seaborn(df):
    with sns.axes_style("whitegrid", SNS_STYLE):
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        sns.lineplot(data=df, x="월", y="판매량", hue="메뉴", style="메뉴",
                     palette=MENU_COLORS, markers=MENU_MARKERS, dashes=False,
                     lw=2, ms=7, mec="white", ax=ax)
        ax.set_title("메뉴별 월간 판매량", fontsize=14, fontweight="bold", color=INK, loc="left")
        ax.set_xlabel("월", color=MUTED)
        ax.set_ylabel("판매량 (잔)", color=MUTED)
        ax.set_xticks(range(1, 13), [f"{m}월" for m in range(1, 13)])
        ax.tick_params(colors=MUTED, labelsize=9)
        sns.despine(ax=ax)
        sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.2), title="메뉴",
                        frameon=False, fontsize=9, ncol=4)
        fig.tight_layout()
    return fig


def cafe_plotly(df):
    fig = px.line(df, x="월", y="판매량", color="메뉴", symbol="메뉴", markers=True,
                  color_discrete_map=MENU_COLORS,
                  labels={"월": "월", "판매량": "판매량 (잔)", "메뉴": "메뉴"},
                  title="메뉴별 월간 판매량")
    fig.update_traces(line_width=2, marker=dict(size=8, line=dict(width=1.5, color="white")),
                      hovertemplate="%{x}월 · %{y:,}잔")
    fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=[f"{m}월" for m in range(1, 13)],
                     showgrid=False, linecolor="#C9C4DA")
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    fig.update_layout(hovermode="x unified")
    return style_plotly(fig)


# -----------------------------------------------------------------------------
# 차트: 데이터 2 — 공부 시간 vs 시험 점수 (산점도)


def study_matplotlib(df):
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for cls, color in CLASS_COLORS.items():
        d = df[df["반"] == cls]
        ax.scatter(d["공부 시간"], d["시험 점수"], s=48, color=color, alpha=0.85,
                   marker=CLASS_MARKERS[cls], edgecolor="white", lw=1.2, label=cls)
    slope, intercept = np.polyfit(df["공부 시간"], df["시험 점수"], 1)
    xs = np.linspace(df["공부 시간"].min(), df["공부 시간"].max(), 50)
    ax.plot(xs, slope * xs + intercept, color=INK, lw=1.5, ls="--", label="전체 추세선")
    ax.set_title("주간 공부 시간과 시험 점수", fontsize=14, fontweight="bold", color=INK, loc="left")
    ax.set_xlabel("주간 공부 시간 (시간)", color=MUTED)
    ax.set_ylabel("시험 점수 (점)", color=MUTED)
    ax.grid(color=GRID)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#C9C4DA")
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.legend(title="반", frameon=False, fontsize=9)
    fig.tight_layout()
    return fig


def study_seaborn(df):
    with sns.axes_style("whitegrid", SNS_STYLE):
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        sns.regplot(data=df, x="공부 시간", y="시험 점수", scatter=False, ax=ax,
                    color=INK, line_kws={"lw": 1.5, "ls": "--"})
        sns.scatterplot(data=df, x="공부 시간", y="시험 점수", hue="반", style="반",
                        palette=CLASS_COLORS, markers=CLASS_MARKERS, s=55, alpha=0.85,
                        edgecolor="white", lw=1.2, ax=ax)
        ax.set_title("주간 공부 시간과 시험 점수", fontsize=14, fontweight="bold", color=INK, loc="left")
        ax.set_xlabel("주간 공부 시간 (시간)", color=MUTED)
        ax.set_ylabel("시험 점수 (점)", color=MUTED)
        ax.tick_params(colors=MUTED, labelsize=9)
        sns.despine(ax=ax)
        sns.move_legend(ax, "lower right", title="반", frameon=False, fontsize=9)
        fig.tight_layout()
    return fig


def study_plotly(df):
    fig = px.scatter(df, x="공부 시간", y="시험 점수", color="반", symbol="반",
                     color_discrete_map=CLASS_COLORS,
                     labels={"공부 시간": "주간 공부 시간 (시간)", "시험 점수": "시험 점수 (점)"},
                     title="주간 공부 시간과 시험 점수")
    fig.update_traces(selector=dict(mode="markers"), opacity=0.85,
                      marker=dict(size=9, line=dict(width=1.2, color="white")),
                      hovertemplate="공부 %{x}시간 · %{y}점")
    slope, intercept = np.polyfit(df["공부 시간"], df["시험 점수"], 1)
    xs = np.array([df["공부 시간"].min(), df["공부 시간"].max()])
    fig.add_scatter(x=xs, y=slope * xs + intercept, mode="lines", name="전체 추세선",
                    line=dict(color=INK, dash="dash", width=1.5), hoverinfo="skip")
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#C9C4DA")
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return style_plotly(fig)


def style_plotly(fig):
    fig.update_layout(
        height=440,
        template="plotly_white",
        font=dict(family="Noto Sans KR, sans-serif", color=MUTED, size=12),
        title=dict(font=dict(size=18, color=INK), x=0.02),
        legend=dict(title_font_color=INK),
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


# -----------------------------------------------------------------------------
# 스타일

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="st-"], .stMarkdown { font-family: 'Noto Sans KR', sans-serif; }
.stApp {
  background:
    radial-gradient(circle at 8% 6%, #FFD6E8 0, transparent 28%),
    radial-gradient(circle at 92% 12%, #D6DEFF 0, transparent 30%),
    radial-gradient(circle at 85% 90%, #FFF0C2 0, transparent 30%),
    radial-gradient(circle at 10% 88%, #C8F5EC 0, transparent 30%),
    #FFFBF5;
}
.block-container { padding-top: 2.2rem; max-width: 1500px; }

.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(120deg, #FF3D8B 0%, #A14BFF 45%, #3D5AFE 100%);
  border: 3px solid #1E1B3A; border-radius: 28px;
  box-shadow: 8px 8px 0 #1E1B3A;
  padding: 2.2rem 2.4rem; color: white; margin-bottom: 2rem;
}
.hero::after {
  content: "★ ✿ ♥ ✦"; position: absolute; right: 2rem; top: 1rem;
  font-size: 2.2rem; letter-spacing: .6rem; opacity: .35;
}
.hero h1 {
  font-family: 'Black Han Sans', sans-serif; font-weight: 400;
  font-size: clamp(2rem, 4vw, 3.2rem); margin: .2rem 0 .4rem; color: white;
  text-shadow: 3px 3px 0 #1E1B3A; padding: 0;
}
.hero p { font-size: 1.05rem; margin: 0; opacity: .95; }
.sticker {
  display: inline-block; background: #FFE14D; color: #1E1B3A;
  border: 2px solid #1E1B3A; border-radius: 999px; padding: .2rem .9rem;
  font-weight: 900; font-size: .8rem; transform: rotate(-3deg);
  box-shadow: 3px 3px 0 #1E1B3A;
}

.lib-card {
  border: 3px solid #1E1B3A; border-radius: 22px; padding: 1.2rem 1.4rem;
  box-shadow: 6px 6px 0 #1E1B3A; height: 100%; color: #1E1B3A;
}
.lib-card h3 { font-family: 'Black Han Sans', sans-serif; font-weight: 400; margin: 0 0 .3rem; font-size: 1.6rem; padding: 0; }
.lib-card .tag { font-size: .85rem; font-weight: 700; opacity: .75; margin-bottom: .6rem; }
.lib-card ul { margin: 0; padding-left: 1.1rem; font-size: .92rem; line-height: 1.65; }
.mpl { background: linear-gradient(135deg, #DCE3FF, #F2F4FF); }
.sns { background: linear-gradient(135deg, #C8F5EC, #EFFFFA); }
.plo { background: linear-gradient(135deg, #FFD6E8, #FFF1F7); }

.section {
  display: flex; align-items: center; gap: .9rem; flex-wrap: wrap;
  margin: 2.6rem 0 .6rem;
}
.section .num {
  font-family: 'Black Han Sans', sans-serif; font-size: 1.6rem;
  width: 3.2rem; height: 3.2rem; border-radius: 50%;
  display: grid; place-items: center; color: white;
  border: 3px solid #1E1B3A; box-shadow: 3px 3px 0 #1E1B3A;
}
.section h2 { font-family: 'Black Han Sans', sans-serif; font-weight: 400; font-size: 2rem; margin: 0; padding: 0; color: #1E1B3A; }
.section .desc { color: #6B6887; font-size: .95rem; flex-basis: 100%; margin-left: 4.1rem; margin-top: -.5rem; }

.chip-row { display: flex; gap: .5rem; flex-wrap: wrap; margin: .2rem 0 1rem 4.1rem; }
.chip {
  background: white; border: 2px solid #1E1B3A; border-radius: 999px;
  padding: .15rem .8rem; font-size: .82rem; font-weight: 700; color: #1E1B3A;
}
.chip b { color: #FF3D8B; }

[class*="st-key-card"] {
  background: white; border: 3px solid #1E1B3A !important; border-radius: 22px;
  box-shadow: 6px 6px 0 #1E1B3A; padding: 1rem 1rem .6rem;
}
.lib-label {
  display: inline-block; font-weight: 900; font-size: .85rem; color: white;
  border: 2px solid #1E1B3A; border-radius: 10px; padding: .15rem .7rem;
  margin-bottom: .4rem;
}

.cmp-wrap { overflow-x: auto; border: 3px solid #1E1B3A; border-radius: 22px; box-shadow: 6px 6px 0 #1E1B3A; background: white; }
.cmp { width: 100%; border-collapse: collapse; font-size: .95rem; color: #1E1B3A; min-width: 640px; }
.cmp th, .cmp td { padding: .8rem 1rem; text-align: left; border-bottom: 1px solid #ECE8F5; }
.cmp thead th { font-family: 'Black Han Sans', sans-serif; font-weight: 400; font-size: 1.1rem; color: white; border-bottom: 3px solid #1E1B3A; }
.cmp thead th:nth-child(1) { background: #1E1B3A; }
.cmp thead th:nth-child(2) { background: #3D5AFE; }
.cmp thead th:nth-child(3) { background: #00A98F; }
.cmp thead th:nth-child(4) { background: #FF3D8B; }
.cmp tbody th { font-weight: 900; background: #FFF7E0; white-space: nowrap; }
.cmp tbody tr:last-child th, .cmp tbody tr:last-child td { border-bottom: none; }
.stars { color: #FFA000; letter-spacing: .1rem; }

.footer { text-align: center; color: #6B6887; font-size: .85rem; margin: 3rem 0 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

LIBS = [
    ("Matplotlib", BLUE, "mpl"),
    ("Seaborn", TEAL, "sns"),
    ("Plotly", PINK, "plo"),
]

# -----------------------------------------------------------------------------
# 헤더

st.markdown(
    """
<div class="hero">
  <span class="sticker">DATA VIZ SHOWDOWN</span>
  <h1>시각화 라이브러리 3대장 비교</h1>
  <p>같은 데이터, 다른 느낌! Matplotlib · Seaborn · Plotly로 그린 그래프를 나란히 놓고 비교해 보세요.</p>
</div>
""",
    unsafe_allow_html=True,
)

intro = [
    ("mpl", "Matplotlib", "🧱 파이썬 시각화의 기본기",
     ["모든 요소를 한 줄씩 직접 제어", "논문·보고서용 정적 이미지에 강함", "코드는 길지만 자유도 최고"]),
    ("sns", "Seaborn", "🌊 통계 그래프를 우아하게",
     ["DataFrame 컬럼명으로 바로 매핑", "hue·style로 그룹 구분이 한 줄", "회귀선·분포 등 통계 기능 내장"]),
    ("plo", "Plotly", "✨ 움직이는 인터랙티브 차트",
     ["마우스 오버·확대·범례 토글 기본 제공", "웹 대시보드에 최적", "Express로 짧은 코드, 빠른 결과"]),
]
for col, (cls, name, tag, points) in zip(st.columns(3, gap="large"), intro):
    col.markdown(
        f"""<div class="lib-card {cls}"><h3>{name}</h3><div class="tag">{tag}</div>
        <ul>{''.join(f'<li>{p}</li>' for p in points)}</ul></div>""",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 데이터별 비교 섹션


def section(num, color, title, desc, chips):
    st.markdown(
        f"""<div class="section"><div class="num" style="background:{color}">{num}</div>
        <h2>{title}</h2><div class="desc">{desc}</div></div>
        <div class="chip-row">{''.join(f'<span class="chip">{c}</span>' for c in chips)}</div>""",
        unsafe_allow_html=True,
    )


def comparison_row(key, df, funcs):
    for col, (name, color, cls), func in zip(st.columns(3, gap="medium"), LIBS, funcs):
        with col, st.container(key=f"card_{key}_{cls}"):
            st.markdown(f'<span class="lib-label" style="background:{color}">{name}</span>',
                        unsafe_allow_html=True)
            chart = func(df)
            if name == "Plotly":
                st.plotly_chart(chart, width="stretch", config={"displaylogo": False})
            else:
                st.pyplot(chart, width="stretch")
                plt.close(chart)
            with st.expander("💻 코드 보기"):
                st.code(inspect.getsource(func), language="python")


section(
    "1", PINK, "카페 메뉴별 월간 판매량",
    "선 그래프 · 계절에 따라 메뉴별 판매량이 어떻게 달라지는지 보여줍니다.",
    [f"<b>{cafe_df['월'].nunique()}</b>개월", f"<b>{cafe_df['메뉴'].nunique()}</b>개 메뉴",
     f"총 <b>{cafe_df['판매량'].sum():,}</b>잔"],
)
with st.expander("📋 데이터 미리보기 — 카페 판매량"):
    st.dataframe(cafe_df.pivot(index="월", columns="메뉴", values="판매량")[list(MENU_COLORS)],
                 width="stretch")
comparison_row("cafe", cafe_df, [cafe_matplotlib, cafe_seaborn, cafe_plotly])

section(
    "2", BLUE, "공부 시간과 시험 점수",
    "산점도 + 추세선 · 공부 시간이 늘수록 점수가 오르는지, 반별 차이는 어떤지 살펴봅니다.",
    [f"학생 <b>{len(study_df)}</b>명", f"<b>{study_df['반'].nunique()}</b>개 반",
     f"평균 <b>{study_df['시험 점수'].mean():.1f}</b>점",
     f"상관계수 <b>{study_df['공부 시간'].corr(study_df['시험 점수']):.2f}</b>"],
)
with st.expander("📋 데이터 미리보기 — 학생 성적"):
    st.dataframe(study_df, width="stretch", height=260)
comparison_row("study", study_df, [study_matplotlib, study_seaborn, study_plotly])

# -----------------------------------------------------------------------------
# 한눈에 비교표

section("★", AMBER, "한눈에 비교하기", "상황에 맞는 라이브러리를 골라 보세요.", [])

rows = [
    ("배우기 쉬움", 2, 4, 4),
    ("세밀한 커스터마이징", 5, 3, 4),
    ("인터랙티브 기능", 1, 1, 5),
    ("통계 시각화", 2, 5, 3),
    ("코드 간결함", 2, 4, 5),
]
stars = lambda n: f'<span class="stars">{"★" * n}{"☆" * (5 - n)}</span>'
extra = [
    ("출력 형태", "정적 이미지 (PNG·PDF)", "정적 이미지 (Matplotlib 기반)", "인터랙티브 HTML"),
    ("추천 용도", "논문·인쇄물, 완벽한 제어", "탐색적 데이터 분석(EDA)", "웹 대시보드·발표"),
]
body = "".join(
    f"<tr><th>{label}</th>{''.join(f'<td>{stars(v)}</td>' for v in vals)}</tr>"
    for label, *vals in rows
) + "".join(
    f"<tr><th>{label}</th>{''.join(f'<td>{v}</td>' for v in vals)}</tr>" for label, *vals in extra
)
st.markdown(
    f"""<div class="cmp-wrap"><table class="cmp">
    <thead><tr><th>항목</th><th>Matplotlib</th><th>Seaborn</th><th>Plotly</th></tr></thead>
    <tbody>{body}</tbody></table></div>
    <div class="footer">♥ 예시 데이터는 무작위로 생성된 가상 데이터입니다 ♥</div>""",
    unsafe_allow_html=True,
)
