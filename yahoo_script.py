import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, request, render_template
import time

# Initialize Flask app
app = Flask(__name__)

# Define function to scrape Yahoo Finance page for a given date
def scrape_yahoo_finance(date):
   
    print("Starting scrape")
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'
            }
    # Build URL for Yahoo Finance page for the given date
    url = f'https://finance.yahoo.com/calendar/earnings?day={date}'
    # Send request to Yahoo Finance page
    r = requests.get(url, headers = headers)
    # Parse HTML content using Beautiful Soup
    soup = BeautifulSoup(r.content, 'html.parser')
    # Find table containing earnings data
    table = soup.find('table', {'class': 'W(100%)'})
    # Extract table data and store in Pandas dataframe
    data = []
    df = None
    if table != None: 
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            stock_symbol = cells[0].text
            eps = cells[4].text
            surprise = cells[6].text
            if eps != '-' or surprise != '-':  
                data.append([stock_symbol, eps, surprise])
        df = pd.DataFrame(data, columns=['Stock Symbol', 'EPS', 'Surprise'])    
        df = df.drop_duplicates(subset=['Stock Symbol'])
    return df

def get_cell_color(val):
    if val.startswith("-") and len(val) > 1:
        return '<span style="color:red">' + val + '</span>'
    elif len(val) > 1:
        return '<span style="color:green">' + val + '</span>'
    else:
        return val
# Define Flask route to handle form submission
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get date input from form
        date = request.form['date']
        html = 'No data found for this date'
        # Scrape Yahoo Finance page for the given date
        df = scrape_yahoo_finance(date)
        if df is not None and not df.empty:
            html = df.to_html(classes='table-striped table-responsive table-bordered table-hover', index=False,  formatters={
                'Surprise': lambda x: get_cell_color(x)}, escape=False)
        # Render template with scraped data
        return render_template('yahoo_index.html', data=html)
    else:
        # Render empty form
        return render_template('yahoo_index.html')

# Run Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)