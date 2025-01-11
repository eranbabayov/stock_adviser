import yfinance as yf
from datetime import datetime

def calc_moving_avg(stock_data, moving_avg: int):
    stocks_moving_avg = {}
    sorted_dates = sorted(stock_data.keys())  # Sort by date in ascending order
    for i in range(moving_avg - 1, len(sorted_dates)):  # Start at index moving_avg - 1
        window = sorted_dates[i - moving_avg + 1:i + 1]  # Take the last `moving_avg` dates
        window_avg = sum(stock_data[date] for date in window) / moving_avg
        stocks_moving_avg[sorted_dates[i]] = window_avg  # Store the average with the current date as key

    return stocks_moving_avg


def get_stock_data_from_yahoo(stocks: list[str], start_date: datetime, end_date: datetime):
    # Ensure that start_date and end_date are formatted correctly as strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Download the stock data from Yahoo Finance
    data = yf.download(stocks, start=start_date_str, end=end_date_str)

    return data

def get_last_day_stock_data(symbols):
    stock_data = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            last_price = data['Close'].iloc[-1]  # Get the last close price
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_price
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close else 0

            stock_data.append({
                'symbol': symbol,
                'last_price': round(last_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return stock_data


def get_stock_close(yahoo_stocks_data, requested_stocks: list[str]):
    stocks_close = {}
    stocks_data = []  # To store the stock data (last price, change, etc.)
    is_one_stock = False
    if len(requested_stocks) == 1:
        is_one_stock = True
    for stock in requested_stocks:
        stock_data = {}
        stock_close = yahoo_stocks_data['Close'] if is_one_stock else yahoo_stocks_data['Close'][stock]
        for date, close_value in stock_close.items():
            stock_data[str(date.date())] = close_value

        sorted_stock_data = dict(
            sorted(stock_data.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'), reverse=True))

        stocks_close[stock] = sorted_stock_data
        stocks_data.append(get_last_day_stock_data([stock])[0])  # Get the stock data for the current stock

    return stocks_close, stocks_data

def check_etf_valid(symbol: str) -> bool:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')

        # Check if the data is empty or has missing values (like NaNs)
        if data.empty or data.isna().all().all():
            print(f"Invalid ETF symbol: {symbol} (No data available)")
            return False

        # If no error occurred, the ETF is valid
        print(f"Valid ETF symbol: {symbol}")
        return True

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return False


if __name__ == '__main__':
    stocks = ['QQQ', 'SPY', 'IWM']
    start_date = datetime(2024, 12, 1)
    end_date = datetime(2025, 1, 4)
    data = get_stock_data_from_yahoo(stocks, start_date, end_date)
    stocks_close, stocks_data = get_stock_close(data, stocks)
    print(stocks_close)
    print("################################")
    moving_averages = {stock: calc_moving_avg(stocks_close[stock], 20) for stock in stocks}
    print(moving_averages)
    print("#####################")
    print(stocks_data)