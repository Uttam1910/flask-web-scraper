import logging
from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get URL from the frontend form
    url = request.json.get('url')  # Match the JS fetch request

    # Validate URL (basic validation)
    if not url or not url.startswith(('http://', 'https://')):
        logging.warning("Invalid URL provided by user.")
        return jsonify({'error': 'Invalid URL. Please provide a valid URL starting with http:// or https://'}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # Request with a timeout for better control
        response = requests.get(url, headers=headers, timeout=10)

        # Check if the request was successful
        if response.status_code != 200:
            logging.error(f'Failed to retrieve data from the URL. Status code: {response.status_code}')
            return jsonify({'error': f'Failed to retrieve data from the URL. Status code: {response.status_code}'}), 400

        soup = BeautifulSoup(response.text, 'html.parser')

        # Example scraping for Amazon - adapt selectors based on the website
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

        logging.info(f'Successfully scraped {len(products)} products.')
        return jsonify({'products': products})

    except requests.exceptions.Timeout:
        logging.error("The request timed out")
        return jsonify({'error': 'The request timed out. Please try again later.'}), 500

    except requests.exceptions.ConnectionError:
        logging.error("Connection error")
        return jsonify({'error': 'Failed to connect. Check the URL or your internet connection.'}), 500

    except requests.exceptions.RequestException as e:
        logging.error(f'RequestException: {str(e)}')
        return jsonify({'error': f'An error occurred while making the request: {str(e)}'}), 500

    except Exception as e:
        logging.error(f'General Exception: {str(e)}')
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
