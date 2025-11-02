import pandas as pd
import altair as alt

# 重新加载第一个文件（处理后的）
df_processed = pd.read_csv('processed_data.csv')

# 重新加载第二个文件（处理前的）
df_unprocessed = pd.read_csv('军工板块2020_01_01——2025_10_17周线数据数据（未清洗）.csv')

# --- 数据准备 ---

# 1. 筛选股票代码 920225
df_proc_stock = df_processed[df_processed['stock_code'] == 920225].copy()
df_unproc_stock = df_unprocessed[df_unprocessed['stock_code'] == 920225].copy()

# 2. 转换日期列为 datetime 对象
df_proc_stock['trade_date'] = pd.to_datetime(df_proc_stock['trade_date'])
df_unproc_stock['trade_date'] = pd.to_datetime(df_unproc_stock['trade_date'])

# 3. 添加一个 'type' 列来区分数据来源
df_proc_stock['type'] = '处理后'
df_unproc_stock['type'] = '处理前'

# 4. 只保留绘图需要的列
df_proc_plot = df_proc_stock[['trade_date', 'close', 'type']]
df_unproc_plot = df_unproc_stock[['trade_date', 'close', 'type']]

# 5. 合并两个 DataFrame
df_combined = pd.concat([df_unproc_plot, df_proc_plot])

# --- 绘图 ---

# 创建基础图表
base = alt.Chart(df_combined).encode(
    x=alt.X('trade_date', title='交易日期'),  # X轴：交易日期
    y=alt.Y('close', title='收盘价'),        # Y轴：收盘价
    color=alt.Color('type', title='数据状态'),   # 颜色：区分处理前后
    tooltip=[
        alt.Tooltip('trade_date', title='日期'),
        alt.Tooltip('close', title='收盘价'),
        alt.Tooltip('type', title='状态')
    ]
)

# 创建折线图
line = base.mark_line().properties(
    title='股票 920225：处理前后收盘价对比' # 图表标题
)

# 创建点图（为了更好的交互）
points = base.mark_point()

# 合并折线和点图，并添加交互
chart = (line + points).interactive()

# 保存图表为 JSON 文件
chart.save('stock_920225_comparison_chart.json')
