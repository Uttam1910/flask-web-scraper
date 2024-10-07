import logging
from flask import Flask, request, render_template, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import csv
import io
import time

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

def fetch_page_with_retries(url, headers, retries=5, delay=2):
    """Fetch the page with retry mechanism if a 503 or other recoverable error occurs."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 503:
                logging.warning(f"503 Error on attempt {attempt + 1}. Retrying in {delay} seconds...")
                time.sleep(delay)  # Exponential backoff
                delay *= 2  # Increase delay
            else:
                return response  # For non-retryable errors, return the response
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
            time.sleep(delay)
            delay *= 2
    return None  # Return None if all attempts fail

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')

    if not url or not url.startswith(('http://', 'https://')):
        logging.warning("Invalid URL provided by user.")
        return jsonify({'error': 'Invalid URL. Please provide a valid URL starting with http:// or https://'}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Fetch the page with retries
    response = fetch_page_with_retries(url, headers)

    if not response:
        logging.error("Failed to retrieve the page after multiple retries.")
        return jsonify({'error': 'Failed to retrieve the page after multiple retries.'}), 500

    if response.status_code != 200:
        logging.error(f"Failed to retrieve data from the URL. Status code: {response.status_code}")
        return jsonify({'error': f"Failed to retrieve data from the URL. Status code: {response.status_code}"}), 400

    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    for product in soup.select('.s-result-item'):
        name = product.select_one('h2 a span')
        price = product.select_one('.a-price-whole')
        rating = product.select_one('.a-icon-alt')

        name_text = name.get_text(strip=True) if name else 'No Name'
        price_text = price.get_text(strip=True) if price else 'N/A'
        rating_text = rating.get_text(strip=True) if rating else 'No Rating'

        products.append({
            'name': name_text,
            'price': price_text,
            'rating': rating_text
        })

    if not products:
        return jsonify({'error': 'No products found on the page.'}), 404

    # Create CSV in-memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['name', 'price', 'rating'])
    writer.writeheader()
    writer.writerows(products)
    output.seek(0)

    # Send JSON response along with CSV download link
    return jsonify({
        'products': products,
        'csv_url': '/download-csv'
    })

@app.route('/download-csv')
def download_csv():
    # CSV content from previous scraping session (just for example)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name', 'price', 'rating'])
    writer.writerow(['Sample Product 1', '100', '4.5'])  # Example row
    writer.writerow(['Sample Product 2', '200', '4.0'])  # Example row

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='scraped_products.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)
