# Stock Adviser

## Overview

The Stock Adviser Web Application is an advanced platform designed to help users manage and analyze their stock portfolios.
With features ranging from stock tracking and analysis to trade management, the application provides a comprehensive toolset 
for making informed investment decisions.
## Features

### User Management
   - Secure Login & Registration
   - Password Management: Password reset via email with secure tokens.
### Stock Management
   - Portfolio Tracking: Users can add or remove stocks from their portfolios.

   - Stock Watchlist: Automatically updates based on user-selected stocks.

   - Performance Analysis: Tracks moving averages (20, 50, 150, 200-day) for each stock.

### Trade Management
   - Trade Recording: Users can log trades with buy/sell prices and dates.
   - Trade History: Displays a detailed record of all user trades.

### Stock Analysis
   - Live Stock Updates: Fetches real-time data for stocks in the user’s portfolio.
   - Performance Insights: Identifies stocks performing above specific moving averages.
## Installation

1. Clone the repository:
    ```
    git clone https://github.com/eranbabayov/stock_adviser.git
    ```
2. Install required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Dependencies

   - Flask

   - Flask-Mail

   - yfinance

   - hashlib