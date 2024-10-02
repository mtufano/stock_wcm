import yfinance as yf

def dcf_analysis(ticker):
    # Fetch stock data
    stock = yf.Ticker(ticker)
    stock_info = stock.info

    # Check if essential data is available
    required_keys = [
        'freeCashflow', 'operatingCashflow', 'totalRevenue', 'ebitda',
        'totalDebt', 'totalCash', 'sharesOutstanding', 'currentPrice',
        'marketCap', 'beta', 'revenueGrowth', 'earningsGrowth'
    ]

    missing_keys = [key for key in required_keys if key not in stock_info or stock_info[key] is None]

    if missing_keys:
        print(f"Missing data for {ticker}: {', '.join(missing_keys)}")
        return None

    # Extract financial data from stock.info
    free_cash_flow = stock_info['freeCashflow']
    operating_cash_flow = stock_info['operatingCashflow']
    total_revenue = stock_info['totalRevenue']
    ebitda = stock_info['ebitda']
    total_debt = stock_info['totalDebt']
    total_cash = stock_info['totalCash']
    shares_outstanding = stock_info['sharesOutstanding']
    current_price = stock_info['currentPrice']
    market_cap = stock_info['marketCap']
    beta = stock_info['beta']
    revenue_growth = stock_info['revenueGrowth']
    earnings_growth = stock_info['earningsGrowth']

    # Set constants
    risk_free_rate = 0.03  # 3% risk-free rate (10-year U.S. Treasury yield)
    market_risk_premium = 0.06  # 6% market risk premium
    tax_rate = 0.21  # 21% corporate tax rate
    terminal_growth_rate = 0.02  # 2% terminal growth rate

    # Calculate Cost of Equity using CAPM
    cost_of_equity = risk_free_rate + beta * market_risk_premium

    # Assume Cost of Debt (Rd)
    cost_of_debt = 0.04  # 4% assumed cost of debt

    # Calculate weights for WACC
    total_value = market_cap + total_debt - total_cash  # Enterprise Value
    weight_of_equity = market_cap / total_value
    weight_of_debt = (total_debt - total_cash) / total_value

    # Calculate WACC
    wacc = (weight_of_equity * cost_of_equity) + (weight_of_debt * cost_of_debt * (1 - tax_rate))

    # Use revenue growth or earnings growth as the FCF growth rate
    if revenue_growth is not None and revenue_growth > 0:
        fcf_growth_rate = revenue_growth
    elif earnings_growth is not None and earnings_growth > 0:
        fcf_growth_rate = earnings_growth
    else:
        fcf_growth_rate = 0.02  # Default to 2% if growth rates are negative or unavailable

    # Project Free Cash Flows for the next 5 years
    projected_fcfs = []
    last_fcf = free_cash_flow
    for i in range(1, 6):
        projected_fcf = last_fcf * (1 + fcf_growth_rate) ** i
        projected_fcfs.append(projected_fcf)

    # Calculate Terminal Value using Gordon Growth Model
    terminal_value = projected_fcfs[-1] * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)

    # Discount future cash flows to present value
    present_value_fcfs = []
    for i, fcf in enumerate(projected_fcfs):
        present_value = fcf / (1 + wacc) ** (i + 1)
        present_value_fcfs.append(present_value)

    # Discount Terminal Value to present value
    present_value_terminal = terminal_value / (1 + wacc) ** 5

    # Calculate Enterprise Value
    enterprise_value = sum(present_value_fcfs) + present_value_terminal

    # Calculate Equity Value
    equity_value = enterprise_value - total_debt + total_cash

    # Calculate Intrinsic Value per Share
    intrinsic_value_per_share = equity_value / shares_outstanding

    # Determine if the stock is undervalued
    undervalued = intrinsic_value_per_share > current_price

    # Output the results
    print(f"Ticker: {ticker}")
    print(f"Intrinsic Value per Share: ${intrinsic_value_per_share:.2f}")
    print(f"Current Market Price: ${current_price:.2f}")
    print(f"Undervalued: {undervalued}")

    return {
        'Ticker': ticker,
        'Intrinsic Value': intrinsic_value_per_share,
        'Current Price': current_price,
        'Undervalued': undervalued
    }


# Example usage
if __name__ == "__main__":
    ticker_input = input("Enter the stock ticker symbol: ").upper()
    dcf_analysis(ticker_input)