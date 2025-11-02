import pandas as pd
import altair as alt
from typing import Optional
import os


def load_and_prepare_data(
    processed_file: str,
    unprocessed_file: str,
    stock_code: int,
    period_type: str = "周线"
) -> pd.DataFrame:
    """
    加载并准备股票数据用于对比分析
    
    Parameters:
    -----------
    processed_file : str
        处理后数据的CSV文件路径
    unprocessed_file : str
        处理前数据的CSV文件路径  
    stock_code : int
        股票代码
    period_type : str, optional
        时间周期类型，默认为"周线"，可选"周线"或"日线"
    
    Returns:
    --------
    pd.DataFrame
        合并后的数据框，包含处理前后的对比数据
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(processed_file):
            raise FileNotFoundError(f"处理后的数据文件不存在: {processed_file}")
        if not os.path.exists(unprocessed_file):
            raise FileNotFoundError(f"处理前的数据文件不存在: {unprocessed_file}")
        
        # 加载数据
        df_processed = pd.read_csv(processed_file)
        df_unprocessed = pd.read_csv(unprocessed_file)
        
        # 验证必要的列是否存在
        required_columns = ['stock_code', 'trade_date', 'close']
        for df, name in [(df_processed, "处理后数据"), (df_unprocessed, "处理前数据")]:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"{name}缺少必要的列: {missing_cols}")
        
        # 筛选指定股票代码
        df_proc_stock = df_processed[df_processed['stock_code'] == stock_code].copy()
        df_unproc_stock = df_unprocessed[df_unprocessed['stock_code'] == stock_code].copy()
        
        # 检查股票数据是否存在
        if df_proc_stock.empty:
            raise ValueError(f"在处理后数据中未找到股票代码 {stock_code}")
        if df_unproc_stock.empty:
            raise ValueError(f"在处理前数据中未找到股票代码 {stock_code}")
        
        # 转换日期列为 datetime 对象
        df_proc_stock['trade_date'] = pd.to_datetime(df_proc_stock['trade_date'])
        df_unproc_stock['trade_date'] = pd.to_datetime(df_unproc_stock['trade_date'])
        
        # 添加数据来源标识
        df_proc_stock['type'] = '处理后'
        df_unproc_stock['type'] = '处理前'
        
        # 只保留绘图需要的列
        df_proc_plot = df_proc_stock[['trade_date', 'close', 'type']]
        df_unproc_plot = df_unproc_stock[['trade_date', 'close', 'type']]
        
        # 合并两个数据框
        df_combined = pd.concat([df_unproc_plot, df_proc_plot], ignore_index=True)
        
        return df_combined
        
    except Exception as e:
        print(f"数据加载和处理过程中出现错误: {e}")
        raise


def create_comparison_chart(
    df_combined: pd.DataFrame,
    stock_code: int,
    period_type: str = "周线",
    output_file: Optional[str] = None
) -> alt.Chart:
    """
    创建处理前后数据对比图表
    
    Parameters:
    -----------
    df_combined : pd.DataFrame
        合并后的数据框
    stock_code : int
        股票代码
    period_type : str, optional
        时间周期类型，默认为"周线"
    output_file : str, optional
        输出文件路径，如果为None则不保存
    
    Returns:
    --------
    alt.Chart
        生成的图表对象
    """
    # 创建基础图表
    base = alt.Chart(df_combined).encode(
        x=alt.X('trade_date', title='交易日期'),
        y=alt.Y('close', title='收盘价'),
        color=alt.Color('type', title='数据状态'),
        tooltip=[
            alt.Tooltip('trade_date', title='日期', format='%Y-%m-%d'),
            alt.Tooltip('close', title='收盘价', format='.2f'),
            alt.Tooltip('type', title='状态')
        ]
    )
    
    # 创建折线图
    line = base.mark_line().properties(
        title=f'股票 {stock_code}：{period_type}处理前后收盘价对比'
    )
    
    # 创建点图（为了更好的交互）
    points = base.mark_point(opacity=0.6, size=30)
    
    # 合并折线和点图，并添加交互
    chart = (line + points).interactive()
    
    # 保存图表
    if output_file:
        chart.save(output_file)
        print(f"图表已保存至: {output_file}")
    
    return chart


def compare_stock_data(
    stock_code: int,
    processed_file: str = '../../../xwechat_files/wxid_jo9dg9bjbasy12_38bf/msg/file/2025-11/processed_data.csv',
    unprocessed_file: str = '../../../xwechat_files/wxid_jo9dg9bjbasy12_38bf/msg/file/2025-11/军工板块2020_01_01——2025_10_17周线数据数据（未清洗）.csv',
    period_type: str = "周线",
    output_file: Optional[str] = None
) -> alt.Chart:
    """
    主函数：比较股票处理前后的数据
    
    Parameters:
    -----------
    stock_code : int
        股票代码
    processed_file : str, optional
        处理后数据的CSV文件路径
    unprocessed_file : str, optional  
        处理前数据的CSV文件路径
    period_type : str, optional
        时间周期类型，默认为"周线"，可选"周线"或"日线"
    output_file : str, optional
        输出文件路径，如果为None则自动生成
    
    Returns:
    --------
    alt.Chart
        生成的图表对象
    """
    # 验证时间周期类型
    if period_type not in ["周线", "日线"]:
        raise ValueError("period_type 必须是 '周线' 或 '日线'")
    
    # 如果未指定输出文件，自动生成文件名
    if output_file is None:
        output_file = f'stock_{stock_code}_{period_type}_comparison_chart.json'
    
    print(f"开始处理股票 {stock_code} 的{period_type}数据对比...")
    
    # 加载和准备数据
    df_combined = load_and_prepare_data(
        processed_file=processed_file,
        unprocessed_file=unprocessed_file,
        stock_code=stock_code,
        period_type=period_type
    )
    
    # 创建图表
    chart = create_comparison_chart(
        df_combined=df_combined,
        stock_code=stock_code,
        period_type=period_type,
        output_file=output_file
    )
    
    print(f"股票 {stock_code} 的{period_type}数据对比图表生成完成！")
    return chart


# 示例用法
if __name__ == "__main__":
    # 使用默认参数生成周线对比图表
    chart_weekly = compare_stock_data(
        stock_code=920225,
        period_type="周线"
    )
    
    # 如果需要生成日线对比图表，可以这样调用：
    # chart_daily = compare_stock_data(
    #     stock_code=920225,
    #     period_type="日线"
    # )
