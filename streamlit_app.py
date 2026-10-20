import streamlit as st
import math
import itertools
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(
    page_title="s[m]n 多次元単体ビジュアライザー",
    page_icon="📐",
    layout="wide"
)

st.title("📐 パスカルの多次元単体 (Simplex) ビジュアライザー")
st.markdown("""
パスカルの三角形の項数を高次元に拡張した **$s[m]n$**（項数 $m$、冪乗 $n$）の数表と、
3次元空間へスライス・投影したインタラクティブな3Dモデル（**拡大縮小・回転可能**）を同時に生成します。
""")

# --- 入力コントロール（ドロップダウン） ---
st.sidebar.header("🎛️ パラメータ設定")
m_options = [2, 3, 4, 5, 6, 7]
n_options = [1, 2, 3, 4, 5, 6]

m_val = st.sidebar.selectbox("項数 m (次元数)", options=m_options, index=2)
n_val = st.sidebar.selectbox("冪乗 n (次数 / 段数 = n + 1)", options=n_options, index=2)

st.sidebar.markdown(f"**現在の設定:** s[{m_val}]{n_val} （段数: {n_val + 1}）")


# --- 数表生成関数 ---
def get_s_table(n_val, m_val):
    def get_coeffs(term_m, power_n):
        if term_m == 1:
            return [1]
        if term_m == 2:
            return [math.comb(power_n, k) for k in range(power_n + 1)]
        slices = []
        for k in range(power_n + 1):
            sub = get_coeffs(term_m - 1, power_n - k)
            scaled = multiply(sub, math.comb(power_n, k))
            slices.append(scaled)
        return slices

    def multiply(struct, factor):
        if isinstance(struct, list):
            return [multiply(item, factor) for item in struct]
        return struct * factor

    def format_struct(struct, term_m):
        if term_m == 2:
            return " ".join(map(str, struct))
        blank_lines = term_m - 2
        separator = "\n" * (blank_lines + 1)
        sub_strs = [format_struct(sub, term_m - 1) for sub in struct]
        return separator.join(sub_strs)

    coeffs = get_coeffs(m_val, n_val)
    return format_struct(coeffs, m_val)


# --- 座標空間生成関数 ---
def generate_coordinate_space(m_val, n_val):
    coords = []
    for partition in itertools.product(range(n_val + 1), repeat=m_val):
        if sum(partition) == n_val:
            num = math.factorial(n_val)
            den = math.prod(math.factorial(k) for k in partition)
            alpha = num // den
            coords.append((*partition, alpha))
    return coords


# --- レイアウト：数表と3Dモデルを並べる ---
tab1, tab2 = st.tabs(["📊 数表データ (2Dテキスト)", "🌐 インタラクティブ3Dモデル"])

with tab1:
    st.subheader(f"s[{m_val}]{n_val} の数表（段数: {n_val + 1}）")
    raw_text = get_s_table(n_val, m_val)
    st.text(raw_text)

with tab2:
    st.subheader(f"s[{m_val}]{n_val} の3D空間投影")
    st.info("💡 **操作方法**: グラフの上でスワイプすると**回転**、ピンチイン/アウトで**拡大縮小**ができます。")
    
    coords = generate_coordinate_space(m_val, n_val)
    
    if m_val <= 4:
        df = pd.DataFrame(coords, columns=[f"x{i+1}" for i in range(m_val)] + ["alpha"])
        while len(df.columns) < 4:
            df[f"x{len(df.columns)}"] = 0
            
        fig = px.scatter_3d(
            df, x='x1', y='x2', z='x3',
            color='alpha',
            size='alpha',
            size_max=18,
            opacity=0.85,
            color_continuousScale='Viridis',
            title=f"s[{m_val}]{n_val} (3D統合表示 / 段数: {n_val + 1})"
        )
        fig.update_layout(scene=dict(
            xaxis_title='x1', yaxis_title='x2', zaxis_title='x3',
            xaxis=dict(range=[0, n_val]),
            yaxis=dict(range=[0, n_val]),
            zaxis=dict(range=[0, n_val])
        ))
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        extra_dims = list(range(3, m_val))
        nested_keys = sorted(list(set(tuple(c[d] for d in extra_dims) for c in coords)))
        
        key_options = [str(k) for k in nested_keys]
        selected_key_str = st.selectbox("📂 階層（スライス層）の選択", options=key_options)
        
        selected_key = nested_keys[key_options.index(selected_key_str)]
        slice_data = [c for c in coords if tuple(c[d] for d in extra_dims) == selected_key]
        
        df = pd.DataFrame(slice_data, columns=[f"x{i+1}" for i in range(m_val)] + ["alpha"])
        
        fig = px.scatter_3d(
            df, x='x1', y='x2', z='x3',
            color='alpha',
            size='alpha',
            size_max=18,
            opacity=0.85,
            color_continuousScale='Viridis',
            title=f"s[{m_val}]{n_val} [階層: {selected_key_str} / 段数: {n_val + 1}]"
        )
        fig.update_layout(scene=dict(
            xaxis_title='x1', yaxis_title='x2', zaxis_title='x3',
            xaxis=dict(range=[0, n_val]),
            yaxis=dict(range=[0, n_val]),
            zaxis=dict(range=[0, n_val])
        ))
        st.plotly_chart(fig, use_container_width=True)