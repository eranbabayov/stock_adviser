# Stock Adviser

## Overview

This project is a stock adviser tool that analyzes historical stock price data and provides insights into the
performance of various stocks over a specified period. It utilizes the Yahoo Finance API to fetch historical stock price
data and performs analysis to identify top-performing stocks based on certain criteria.

## Features

- Fetches historical stock price data using the Yahoo Finance API.
- Analyzes stock performance over a specified period.
- Identifies top-performing stocks based on predefined criteria.
- Generates plots to visualize stock performance trends.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/eranbabayov/stock_adviser.git
    ```
2. Install required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Run the `stock_adviser.py` script to execute the stock adviser tool:
    ```
    python stock_adviser.py
    ```
2. Follow the prompts to specify the scanning days and other parameters.
3. The tool will fetch historical stock price data, analyze the performance of various stocks, and generate
   visualizations to aid in decision-making.

## Dependencies

- yfinance
- pandas
- matplotlib

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull
request with your changes.