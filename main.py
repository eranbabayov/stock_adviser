from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json


class StocksMaster:
    def __init__(self, data, stocks_df, scanning_days):
        self.top_stocks = None
        self.stocks_percentage: dict = {}
        self.data: pd.DataFrame = data
        self.scanning_days: int = scanning_days
        self.stocks_near_avg200: list = []
        self.stocks_near_avg150: list = []
        self.stocks_near_avg50: list = []
        self.stocks_near_avg20: list = []
        self.second_place_stocks: list
        self.top_stocks: list
        self.print_start_end_days: bool = True
        self.stocks_df: pd.DataFrame = stocks_df

    class Config:
        arbitrary_types_allowed = True

    def get_stocks_above_avg(self, avg_day):
        df_columns = self.stocks_df.columns

        for stock in stocks:
            df = data['Close'][stock].copy()  # Make a copy of the DataFrame to avoid SettingWithCopyWarning
            df[f'{avg_day}_day_avg'] = df.rolling(window=avg_day).mean()
            df.dropna(inplace=True)
            last_date = datetime.now() - timedelta(days=self.scanning_days)
            avg_df = df[df.index.isin(df[f'{avg_day}_day_avg'].index)]
            past_days_df = avg_df[avg_df.index >= last_date]
            avg_df = avg_df[(avg_df >= (df[f'{avg_day}_day_avg'])) & (
                    avg_df <= (df[f'{avg_day}_day_avg'] * 1.04))]
            avg_df = avg_df[avg_df.index >= last_date]
            if len(avg_df) > 0:
                self.calculate_percentage_changed(stock_prices=past_days_df, stock=stock)
                match avg_day:
                    case 20:
                        self.stocks_near_avg20.append(stock)
                    case 50:
                        self.stocks_near_avg50.append(stock)
                    case 150:
                        self.stocks_near_avg150.append(stock)
                    case 200:
                        self.stocks_near_avg200.append(stock)
                self.stocks_df[stock] = avg_df
        self.stocks_df = self.stocks_df.dropna(axis=1, how='all')
        self.stocks_df.to_excel(f"stocks_above_{avg_day}_day_avg.xlsx")
        self.stocks_df = pd.DataFrame(columns=df_columns)

    def calculate_percentage_changed(self, stock_prices, stock):
        start_price = stock_prices.iloc[0]
        end_price = stock_prices.iloc[-1]
        percentage_change = ((end_price - start_price) / start_price) * 100
        self.stocks_percentage[stock] = percentage_change
        if self.print_start_end_days:
            print(f"stocks % change from date: {stock_prices.index[0]} - {stock_prices.index[-1]}")
            self.print_start_end_days = False

    def find_best_stocks(self):
        self.stocks_percentage = dict(sorted(self.stocks_percentage.items(), key=lambda item: item[1], reverse=True))

        # Extract the top stocks
        self.top_stocks = list(set(self.stocks_near_avg150) & set(self.stocks_near_avg200))

        print("Top Stocks :", *self.top_stocks)
        # print("Second Place Stocks:", *self.second_place_stocks)
        print(f"stocks percentage change in the past {self.scanning_days} days: {self.stocks_percentage}")

    def save_stocks_plt(self):
        # Define colors for each stock
        fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(12, 20))
        colors = list(mcolors.TABLEAU_COLORS.values())
        data_copy = data.copy()
        top_stocks_with_max_percentage_change = {}
        for stock in self.top_stocks:
            top_stocks_with_max_percentage_change[stock] = self.stocks_percentage[stock]
        top_stocks_with_max_percentage_change = sorted(top_stocks_with_max_percentage_change.items(),
                                                       key=lambda item: item[1], reverse=True)

        # Plot for top stocks
        for i, stock in enumerate(top_stocks_with_max_percentage_change[:5]):
            ax = axes[i]
            ax.plot(data_copy['Close'].index, data_copy['Close'][stock[0]], label=stock, color=colors[i % len(colors)],
                    linewidth=1.5)

            # Calculate 150-day moving average
            data_copy['150MA_' + stock[0]] = data_copy['Close'][stock[0]].rolling(window=150).mean()
            ax.plot(data_copy['Close'].index, data_copy['150MA_' + stock[0]], color=colors[i % len(colors)],
                    linestyle='--',
                    linewidth=1)

            ax.set_xlabel('Date', fontsize=12)  # Increase fontsize for better visibility
            ax.set_ylabel('Closing Price', fontsize=12)  # Increase fontsize for better visibility
            ax.set_title(f'Stock Performance in the past {self.scanning_days} days: {stock[0]} changed {stock[1]:.3f}%',
                         fontsize=14)  # Increase fontsize for better visibility
            ax.legend(loc='upper left', fontsize=10)  # Increase fontsize for better visibility
            ax.grid(True)

        plt.tight_layout()

        # Save the plot as a file (e.g., PNG, PDF, SVG, etc.)
        plt.savefig(f'best_stocks({datetime.now().strftime("%d.%m.%Y")}).png')  # Save as PNG file

        # Clear current figure
        plt.clf()

    def find_me_some_stocks(self):
        # self.get_stocks_above_avg(avg_day=20)
        # self.get_stocks_above_avg(avg_day=50)
        self.get_stocks_above_avg(avg_day=150)
        self.get_stocks_above_avg(avg_day=200)
        self.find_best_stocks()
        self.save_stocks_plt()


if __name__ == '__main__':
    # Define a list of tech stock symbols
    with open("stocks.json", "r") as file:
        stocks = json.load(file)["stocks"]
    # Fetch historical stock price data
    data = yf.download(stocks, start='2023-01-01', end=datetime.today())
    stocks_df = pd.DataFrame(columns=stocks)
    stock_instance = StocksMaster(data=data, stocks_df=stocks_df, scanning_days=10)
    stock_instance.find_me_some_stocks()
