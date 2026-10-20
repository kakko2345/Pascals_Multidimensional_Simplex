import math
import itertools
import streamlit as st
import matplotlib.pyplot as plt

# 日本語フォント対応
plt.rcParams['font.family'] = ['MS Gothic', 'Meiryo', 'sans-serif']

# ページ設定
st.set_page_config(
    page_title="s[m]n 多次元単体ビジュアライザー",
    page_icon="📐",
    layout="wide"
)

st.title("📐 パスカルの多次元単体 (Simplex) ビジュアライザー")
st.markdown("""
パスカルの三角形の項数を高次元に拡張した **$s[m]n$** の構造を、3次元空間へスライス・投影してインタラクティブに可視化します。
""")

# --- サイドバーの設定 ---
st.sidebar.header("⚙️ パラメータ設定")
m_val = st.sidebar.slider("項数 m (次元数)", min_value=2, max_value=6, value=3)
n_val = st.sidebar.slider("冪乗 n (段数 = n + 1)", min_value=1, max_value=6, value=3)

# データ生成関数
@st.cache_data
def generate_coordinate_space(m, n):
    coords = []
    for partition in itertools.product(range(n + 1), repeat=m):
        if sum(partition) == n:
            num = math.factorial(n)
            den = math.prod(math.factorial(k) for k in partition)
            alpha = num // den
            coords.append((*partition, alpha))
    return coords

coords = generate_coordinate_space(m_val, n_val)
level_val = n_val + 1

st.subheader(f"📊 s[{m_val}]{n_val} の可視化 (段数: {level_val})")

# --- 可視化処理 ---
if m_val <= 4:
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    zs = [c[2] if m_val >= 3 else 0 for c in coords]
    alphas = [c[-1] for c in coords]
    
    scatter = ax.scatter(xs, ys, zs, c=alphas, s=[a * 20 for a in alphas], cmap='viridis', depthshade=True)
    ax.set_title(f"s[{m_val}]{n_val} (段数: {level_val})", fontsize=12)
    ax.set_xlabel("X (x1)")
    ax.set_ylabel("Y (x2)")
    ax.set_zlabel("Z (x3)")
    fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5, label="alpha")
    
    st.pyplot(fig)
else:
    # m >= 5 の場合の階層スライス
    extra_dims = list(range(3, m_val))
    nested_keys = sorted(list(set(tuple(c[d] for d in extra_dims) for c in coords)))
    
    num_plots = len(nested_keys)
    cols = min(2, num_plots)
    rows = math.ceil(num_plots / cols)
    
    fig = plt.figure(figsize=(6 * cols, 5 * rows))
    
    for i, key in enumerate(nested_keys):
        slice_data = [c for c in coords if tuple(c[d] for d in extra_dims) == key]
        
        xs = [c[0] for c in slice_data]
        ys = [c[1] for c in slice_data]
        zs = [c[2] for c in slice_data]
        alphas = [c[-1] for c in slice_data]
        
        ax = fig.add_subplot(rows, cols, i + 1, projection='3d')
        
        if xs and ys and zs:
            scatter = ax.scatter(xs, ys, zs, c=alphas, s=[a * 20 for a in alphas], cmap='viridis', depthshade=True)
            fig.colorbar(scatter, ax=ax, shrink=0.5, aspect=5, label="alpha")
            
        layer_name = f"{m_val}次層数"
        layer_desc = ", ".join([f"x{d+1}={val}" for d, val in zip(extra_dims, key)])
        title_str = f"s[{m_val}]{n_val} (段数: {level_val})\n[{layer_name}: {layer_desc}]"
            
        ax.set_title(title_str, fontsize=10)
        ax.set_xlabel("X (x1)")
        ax.set_ylabel("Y (x2)")
        ax.set_zlabel("Z (x3)")
        ax.set_xlim(0, n_val)
        ax.set_ylim(0, n_val)
        ax.set_zlim(0, n_val)
        
    plt.tight_layout()
    st.pyplot(fig)

# 座標データのテキスト表示
with st.expander("📋 座標データ (Raw Data) を確認する"):
    st.write(f"合計点数: {len(coords)} 点")
    for c in coords:
        st.text(str(c))