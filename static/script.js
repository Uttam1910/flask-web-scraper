document.getElementById('scrape-form').addEventListener('submit', async function (event) {
    event.preventDefault();  // Prevent page refresh

    const url = document.getElementById('url').value.trim(); // Trim whitespace
    const loadingIndicator = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');

    loadingIndicator.style.display = 'block';  // Show loading
    resultsDiv.innerHTML = '';  // Clear previous results

    try {
        // Validate URL format
        if (!url || !(url.startsWith('http://') || url.startsWith('https://'))) {
            displayError('Please enter a valid URL starting with http:// or https://');
            loadingIndicator.style.display = 'none';  // Hide loading
            return;
        }

        // Send POST request to the backend with the URL
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();
        loadingIndicator.style.display = 'none';  // Hide loading

        if (response.ok) {
            displayResults(data.products);
        } else {
            displayError(data.error);
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';  // Hide loading
        console.error('Error:', error);
        displayError('An unexpected error occurred. Please try again later.');
    }
});

function displayResults(products) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (products.length === 0) {
        resultsDiv.innerHTML = '<p>No products found.</p>';
        return;
    }

    products.forEach(product => {
        const productDiv = document.createElement('div');
        productDiv.classList.add('product');

        productDiv.innerHTML = `
            <h2>${product.name}</h2>
            <p>Price: ${product.price}</p>
            <p>Rating: ${product.rating}</p>
        `;

        resultsDiv.appendChild(productDiv);
    });
}

function displayError(errorMessage) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<p style="color: red;">Error: ${errorMessage}</p>`;
}
