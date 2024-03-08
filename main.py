from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pydantic import BaseModel

 
class StocksMaster(BaseModel):
    stocks_percentage: dict = {}
    stocks_above_150_and_200: list = []
    data: pd.DataFrame
    scanning_days: int
    stocks_near_avg200: list = None
    stocks_near_avg150: list = None
    stocks_near_avg50: list = None
    stocks_near_avg20: list = None
    second_place_stocks: list = None
    top_stocks: list = None
    print_start_end_days: bool = True

    class Config:
        arbitrary_types_allowed = True

    def get_stocks_above_avg(self, avg_day):
        close_to_day_avg = pd.DataFrame()

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
                if avg_day == 150 or avg_day == 200:
                    self.calculate_percentage_changed(stock_prices=past_days_df, stock=stock)
                avg_df['Symbol'] = stock
                close_to_day_avg = pd.concat([close_to_day_avg, avg_df])
                self.stocks_above_150_and_200.append(stock)
        close_to_day_avg.to_excel(f"stocks_above_{avg_day}_day_avg.xlsx")

    # def stocks_near_avg(self, avg_day) -> list:
    #     good_stocks = []
    #     separator = "#" * 72
    #     spaces = " " * 30
    #     print(f"{separator}\n{spaces}avg{avg_day} day\n{separator}")
    #     close_to_day_avg = pd.DataFrame()
    #     try:
    #         for stock in stocks:
    #             df = data['Close'][stock].copy()  # Make a copy of the DataFrame to avoid SettingWithCopyWarning
    #             df[f'{avg_day}_day_avg'] = df.rolling(window=avg_day).mean()
    #             df.dropna(inplace=True)
    #             df_avg = df[df.index.isin(df[f'{avg_day}_day_avg'].index)]
    #             df_avg = df_avg[(df_avg > (df[f'{avg_day}_day_avg'] * 0.98)) & (
    #                     df_avg < (df[f'{avg_day}_day_avg'] * 1.02))]  # Within 2% of the 150-day moving average
    #             last_month_date = datetime.now() - timedelta(days=self.scanning_days)
    #             df_avg = df_avg[df_avg.index >= last_month_date]
    #             if len(df_avg) > 0:
    #                 print(
    #                     f"{stock} date: {df_avg.index[-1]} value: {df_avg.iloc[-1]}")
    #                 if avg_day == 20:
    #                     self.calculate_percentage_changed(stock_prices=df_avg, stock=stock)
    #                 good_stocks.append(stock)
    #                 df_avg['Symbol'] = stock
    #                 close_to_day_avg = pd.concat([close_to_day_avg, df_avg])
    #         close_to_day_avg.to_excel(f"stocks_near_to_{avg_day}_avg.xlsx")
    #     except Exception as ex:
    #         raise Exception(f"FAIL! {ex}")
    #     return good_stocks

    def calculate_percentage_changed(self, stock_prices, stock):
        start_price = stock_prices.iloc[0]
        end_price = stock_prices.iloc[-1]
        percentage_change = ((end_price - start_price) / start_price) * 100
        self.stocks_percentage[stock] = percentage_change
        if self.print_start_end_days:
            print(f"stocks % change from date: {stock_prices.index[0]} - {stock_prices.index[-1]}")
            self.print_start_end_days = False

    def find_best_stocks(self):
        # Find common stocks across all lists

        # Find stocks in at least one list
        # all_stocks = set(self.stocks_near_avg20) | set(self.stocks_near_avg50) | set(self.stocks_near_avg150) | set(
        #     self.stocks_near_avg200)

        # Sort stocks based on frequency
        self.stocks_percentage = sorted(self.stocks_percentage.items(), key=lambda item: item[1], reverse=True)
        # Extract the top stocks
        self.top_stocks = self.stocks_above_150_and_200
        print("Stocks above 150avg or 200:", *self.stocks_above_150_and_200)
        print("Top Stocks :", *self.top_stocks)
        # print("Second Place Stocks:", *self.second_place_stocks)
        print(f"stocks percentage change in the past {self.scanning_days} days: {self.stocks_percentage}")

    def save_stocks_to_plt(self):
        # Define colors for each stock
        colors = list(mcolors.TABLEAU_COLORS.values())
        data_copy = data.copy()
        # Plot for top stocks
        for i, stock in enumerate(self.top_stocks):
            plt.plot(data_copy['Close'].index, data_copy['Close'][stock], label=stock, color=colors[i % len(colors)],
                     linewidth=1.5)

            # Calculate 20-day moving average
            data_copy['20MA_' + stock] = data_copy['Close'][stock].rolling(window=150).mean()
            plt.plot(data_copy['Close'].index, data_copy['20MA_' + stock], color=colors[i % len(colors)],
                     linestyle='--',
                     linewidth=1)

        plt.xlabel('Date')
        plt.ylabel('Closing Price')
        plt.title(f'Top Stocks Performance ({datetime.now().strftime("%d.%m.%Y")})')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # Place legend to the right of the plot
        plt.xticks(rotation=90)  # Rotate dates for better readability
        plt.grid(True)
        plt.tight_layout()

        # Save the plot as a file (e.g., PNG, PDF, SVG, etc.)
        plt.savefig(f'best_stocks({datetime.now().strftime("%d.%m.%Y")}).png')  # Save as PNG file

        # Clear current figure
        plt.clf()

        # Plot for second place stocks
        # for i, stock in enumerate(self.second_place_stocks):
        #     plt.plot(data_copy['Close'].index, data_copy['Close'][stock], label=stock, color=colors[i % len(colors)],
        #              linewidth=1.5)
        #
        #     # Calculate 20-day moving average
        #     data_copy['20MA_' + stock] = data_copy['Close'][stock].rolling(window=150).mean()
        #     plt.plot(data_copy['Close'].index, data_copy['20MA_' + stock], color=colors[i % len(colors)],
        #              linestyle='--',
        #              linewidth=1)
        #
        # plt.xlabel('Date')
        # plt.ylabel('Closing Price')
        # plt.title(f'Second Place Stocks Performance ({datetime.now().strftime("%d.%m.%Y")})')
        #
        # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # Place legend to the right of the plot
        # plt.xticks(rotation=90)  # Rotate dates for better readability
        # plt.grid(True)
        # plt.tight_layout()
        #
        # # Save the plot as a file (e.g., PNG, PDF, SVG, etc.)
        # plt.savefig(f'second_place_stocks({datetime.now().strftime("%d.%m.%Y")}).png')  # Save as PNG file
        #
        # plt.close('all')  # Close all open figures

    def find_me_some_stocks(self):
        # self.get_stocks_above_avg(avg_day=20)
        # self.get_stocks_above_avg(avg_day=50)
        self.get_stocks_above_avg(avg_day=150)
        self.get_stocks_above_avg(avg_day=200)
        self.find_best_stocks()
        self.save_stocks_to_plt()


if __name__ == '__main__':
    # Define a list of tech stock symbols
    stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'ARKK', 'PLTR', 'TSLA', 'COIN', 'XPEV',
              'AFRM', 'UPST', 'MARA', 'NFLX', 'NVDA', 'AMD', 'DIS', 'ROKU', 'SHOP', 'U', 'NVDA', 'ABNB', 'CRWD', 'MELI',
              'TSM', 'PATH', 'DLO', 'PYPL', 'ADBE', 'HD', 'RCL', 'V', 'UNH', 'UBER']
    # stocks = [
    #     'SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOG', 'AMZN', 'META', 'ARKK', 'PLTR', 'TSLA',
    #     'COIN', 'XPEV', 'AFRM', 'UPST', 'MARA', 'NFLX', 'NVDA', 'AMD', 'DIS', 'ROKU',
    #     'SHOP', 'U', 'ABNB', 'CRWD', 'MELI', 'TSM', 'PATH', 'DLO', 'PYPL', 'ADBE',
    #     'HD', 'RCL', 'V', 'UNH', 'UBER', 'BRK-B', 'JPM', 'JNJ', 'PG', 'HD', 'MA', 'V',
    #     'CMCSA', 'VZ', 'XOM', 'CRM', 'PFE', 'INTC', 'CSCO', 'WMT', 'MRK', 'T', 'ABT',
    #     'BABA', 'BMY', 'NVS', 'ORCL', 'CVX', 'DHR', 'ASML', 'NKE', 'TMO', 'KO', 'MCD',
    #     'AVGO', 'TMUS', 'QCOM', 'LLY', 'SBUX', 'NVO', 'ACN', 'TXN', 'PM', 'UNP', 'IBM',
    #     'AMGN', 'CHTR', 'LIN', 'COST', 'ABBV', 'INTU', 'DEO', 'DUK', 'NEE', 'FIS', 'CAT',
    #     'MMM', 'LMT', 'UPS', 'RTX', 'NOW', 'LOW', 'RY', 'COP', 'GS', 'HON', 'BLK', 'MMC',
    #     'BKNG', 'CMG', 'SPGI', 'ISRG', 'ZTS', 'MO', 'BA', 'FDX', 'CVS', 'D', 'PEP', 'SRE',
    #     'MCO', 'SNY', 'ECL', 'TM', 'ICE', 'BUD', 'VLO', 'DOW', 'CI', 'CSX', 'WBA',
    #     'HUM', 'BDX', 'WM', 'LHX', 'NEM', 'DOCU', 'JCI', 'AMAT', 'SQ',
    #     'EPAM', 'TRMB', 'AAL', 'PLUG', 'Z', 'GILD', 'HAL', 'SCHW', 'TDOC', 'PDD',
    #     'GE', 'EBAY', 'ZM', 'DDOG', 'SNAP', 'DAL', 'UAL', 'SLB', 'FCX', 'GM', 'MS', 'INVZ',
    #     'SNOW', 'LUV', 'SOFI', 'MU', 'ADI', 'KLAC', 'WDC', 'SWKS', 'QRVO', 'LRCX', 'MPWR',
    #     'ASML', 'CDNS', 'AVGO', 'QCOM', 'NXPI', 'MCHP', 'APH', 'ANSS', 'VRSN', 'TTWO',
    #     'NTAP', 'CDW', 'KEYS', 'FTNT', 'ZBRA', 'TER', 'FFIV', 'SNPS', 'FLT', 'GDDY',
    #     'ANET', 'TYL', 'FTV', 'ZS', 'BR', 'DDOG', 'TWLO', 'OKTA', 'AYX', 'PANW',
    #     'NOW', 'NET', 'CRWD', 'SPLK', 'DOCU', 'PINS', 'ZM', 'ROKU', 'SNOW', 'SHOP',
    #     'SQ', 'UBER', 'LYFT', 'SPOT', 'GME', 'FSLY', 'PTON', 'CRSP', 'NVTA',
    #     'TDOC', 'EDIT', 'REGN', 'IONS', 'BEAM', 'CERS', 'AMGN', 'BMRN', 'VRTX',
    #     'UTHR', 'BLUE', 'ILMN', 'NBIX', 'ALNY', 'INCY', 'BIIB', 'EXAS',
    #     'GH', 'CDNA', 'PACB', 'VCEL', 'CGEN', 'ONVO'
    # ]

    # Fetch historical stock price data
    data = yf.download(stocks, start='2023-01-01', end=datetime.today())
    stock_instance = StocksMaster(data=data, avg_day=150, scanning_days=5)
    stock_instance.find_me_some_stocks()
