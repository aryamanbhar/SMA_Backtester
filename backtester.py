import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Parameters
TICKER = "AAPL"
START_DATE = "2022-01-01"
END_DATE = "2023-01-01"
SMA_SHORT = 20
SMA_LONG = 50
INITIAL_CASH = 10_000

def fetch_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data['Close']

def generate_signals(prices, sma_short, sma_long):
    df = pd.DataFrame(prices)
    df.columns = ['Close']
    df['SMA_Short'] = df['Close'].rolling(window=sma_short).mean()
    df['SMA_Long'] = df['Close'].rolling(window=sma_long).mean()
    df['Signal'] = 0
    df['Signal'][sma_long:] = (df['SMA_Short'][sma_long:] > df['SMA_Long'][sma_long:]).astype(int)
    df['Position'] = df['Signal'].diff()
    return df

def backtest(df, initial_cash):
    cash = initial_cash
    shares = 0
    history = []
    for i in range(len(df)):
        price = df['Close'].iloc[i]
        pos_change = df['Position'].iloc[i]
        # Buy signal
        if pos_change == 1:
            shares = cash // price
            cash -= shares * price
            action = 'BUY'
        # Sell signal
        elif pos_change == -1 and shares > 0:
            cash += shares * price
            shares = 0
            action = 'SELL'
        else:
            action = '-'
        portfolio_value = cash + shares * price
        history.append({'Date': df.index[i], 'Cash': cash, 'Shares': shares, 'Portfolio': portfolio_value, 'Action': action})
    return pd.DataFrame(history)

def plot_results(prices, df, history):
    plt.figure(figsize=(12,6))
    plt.plot(prices, label='Close Price')
    plt.plot(df['SMA_Short'], label=f'SMA {SMA_SHORT}')
    plt.plot(df['SMA_Long'], label=f'SMA {SMA_LONG}')
    buys = history[history['Action'] == 'BUY']
    sells = history[history['Action'] == 'SELL']
    plt.scatter(buys['Date'], prices.loc[buys['Date']], marker='^', color='g', label='Buy Signal')
    plt.scatter(sells['Date'], prices.loc[sells['Date']], marker='v', color='r', label='Sell Signal')
    plt.title(f"{TICKER} SMA Crossover Backtest")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.show()

def main():
    prices = fetch_data(TICKER, START_DATE, END_DATE)
    df = generate_signals(prices, SMA_SHORT, SMA_LONG)
    history = backtest(df, INITIAL_CASH)
    print(history.tail())
    print(f"Final Portfolio Value: ${history['Portfolio'].iloc[-1]:.2f}")
    plot_results(prices, df, history)

if __name__ == "__main__":
    main()