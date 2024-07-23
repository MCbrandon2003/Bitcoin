import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import os

def read_json_file(file_path):
    """读取JSON文件并返回数据"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def save_json_file(json_dict, file_path):
    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(json_dict, outfile, ensure_ascii=False, indent=4)


import numpy as np

def plot_trades(prices, trades, start_date):
    fig, ax = plt.subplots()
    dates = [index.strftime('%Y-%m-%d') for index in prices.index]
    values = prices['close'].tolist()
    map = {}
    for date, value in zip(dates, values):
        map[date] = value

    ax.plot(dates, values, label='Price')

    for trade in trades:
        if trade[1] == 'buy':
            ax.plot(trade[0], map[trade[0]], 'ro')
            ax.text(trade[0], map[trade[0]], f'Buy {int(trade[3])}', color='red', fontsize=8, ha='right')
        elif trade[1] == 'sell':
            ax.plot(trade[0], map[trade[0]], 'go')
            ax.text(trade[0], map[trade[0]], f'Sell {int(trade[3])}', color='green', fontsize=8, ha='right')

    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title(f'Trades for {start_date}')
    ax.legend()

    if not os.path.exists('./graph'):
        os.makedirs('./graph')

    plt.savefig(f'./graph/{start_date}.png')
    plt.close()

def grid_trading(prices, history_prices, increment_factor, initial_buy_amount, initial_sell_amount,
                 initial_balance, initial_holdings, value, last_buy_price, last_sell_price):
    balance = initial_balance
    holdings = initial_holdings
    current_price = prices[0]
    buy_amount = initial_buy_amount
    sell_amount = initial_sell_amount
    trades = []  # 记录交易

    grid_size = calculate_grid_size(history_prices)
    print(f"Grid size: {grid_size}")

    # 初始网格位置
    last_grid_price = (current_price // grid_size) * grid_size

    for new_price, date in zip(prices.values[1:], prices.index[1:]):
        # 计算新的网格位置
        new_grid_price = (new_price // grid_size) * grid_size

        # 如果价格跨越了网格位置
        if new_grid_price != last_grid_price:
            # 价格下跌，执行买入操作
            if new_price < last_grid_price:
                if last_sell_price is None or new_price < last_sell_price:
                    cost = new_price * buy_amount
                    if balance >= cost:
                        balance -= cost
                        holdings += buy_amount
                        trades.append((date.strftime('%Y-%m-%d'), 'buy', new_price, buy_amount))
                        buy_amount *= increment_factor
                        if sell_amount > initial_sell_amount:
                            sell_amount /= 1.414
                            sell_amount = max(sell_amount, initial_sell_amount)
                        last_buy_price = new_price

            # 价格上涨，执行卖出操作
            elif new_price > last_grid_price:
                if last_buy_price is None or new_price > last_buy_price:
                    if holdings >= sell_amount:
                        revenue = new_price * sell_amount
                        balance += revenue
                        holdings -= sell_amount
                        trades.append((date.strftime('%Y-%m-%d'), 'sell', new_price, sell_amount))
                        sell_amount *= increment_factor
                        if buy_amount > initial_buy_amount:
                            buy_amount /= 1.414
                            buy_amount = max(buy_amount, initial_buy_amount)
                        last_sell_price = new_price

            # 更新网格位置
            last_grid_price = new_grid_price
            current_price = new_price

    # 计算最终利润
    final_value = balance + holdings * current_price
    profit = final_value - value
    profit_rate = profit / value * 100

    return {
        'final_balance': balance,
        'final_holdings': holdings,
        'final_value': final_value,  # 添加总资产数额
        'profit': profit,
        'profit_rate': profit_rate,
        'trades': trades
    }, last_buy_price, last_sell_price, buy_amount, sell_amount


def calculate_grid_size(prices):
    high = prices['high'].max()
    low = prices['low'].min()
    grid_size = (high - low) / 4
    return grid_size


def get_trade_result(filename, history_start_date, history_end_date, start_date, end_date, hold, balance, value,
                     last_buy_price, last_sell_price, buy_amount, sell_amount):
    data_dict = read_json_file(filename)
    df = pd.DataFrame(data_dict['data'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df.set_index('date', inplace=True)

    df_filtered = df.loc[start_date:end_date]
    df_history = df.loc[history_start_date:history_end_date]
    trade_result, last_buy_price, last_sell_price, buy_amount, sell_amount \
        = grid_trading(df_filtered['close'], df_history, 2, buy_amount, sell_amount, balance, hold, value,
                       last_buy_price, last_sell_price)
    print(trade_result)
    save_json_file(trade_result, f"documents/{start_date}.json")

    # Call plot_trades to generate the plot
    plot_trades(df_filtered, trade_result['trades'], start_date)

    return trade_result["final_holdings"], trade_result["final_balance"], trade_result["final_value"], \
           last_buy_price, last_sell_price, buy_amount, sell_amount


if __name__ == '__main__':
    date_list = ['2022-12-01', '2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01',
                 '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01', '2024-01-01']
    filename = "DOT-USD_daily.json"
    # date_list = ['2024-04-01', '2024-05-01', '2024-06-01',
    #              '2024-07-01']

    hold = 0
    balance = 100000
    value = balance
    initial_buy_amount = 2000
    initial_sell_amount = 2000
    buy_amount = initial_buy_amount
    sell_amount = initial_sell_amount
    last_buy_price = None
    last_sell_price = None
    for i in range(len(date_list)-2):
        history_start_date = date_list[i]
        history_end_date = date_list[i+1]
        start_date = date_list[i+1]
        end_date = date_list[i+2]
        last_value = value
        hold, balance, value, last_buy_price, last_sell_price, buy_amount, sell_amount\
            = get_trade_result(filename, history_start_date, history_end_date,
                            start_date, end_date, hold, balance, value,
                            last_buy_price, last_sell_price, buy_amount, sell_amount)
        if value >= last_value:
            last_buy_price = None
            last_sell_price = None
            buy_amount = initial_buy_amount
            sell_amount = initial_sell_amount

        hold = 0
        balance = value

