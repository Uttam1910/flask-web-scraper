document.getElementById('scrape-form').addEventListener('submit', async function (event) {
    event.preventDefault();  // Prevent page refresh

    const url = document.getElementById('url').value.trim(); // Trim whitespace
    const loadingIndicator = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');
    const downloadLinkDiv = document.getElementById('download-link');
    const csvDownloadLink = document.getElementById('csv-download');

    // Show loading indicator and reset previous results and messages
    loadingIndicator.style.display = 'block';  // Show loading
    resultsDiv.innerHTML = '';  // Clear previous results
    errorMessage.style.display = 'none';  // Hide previous error messages
    downloadLinkDiv.style.display = 'none';  // Hide previous download link

    try {
        // Validate URL format using regex for better validation
        const urlPattern = /^(https?:\/\/)[^\s/$.?#].[^\s]*$/i;
        if (!url || !urlPattern.test(url)) {
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
            setupCSVDownload(data.csv_file);
        } else {
            displayError(data.error || 'An unknown error occurred.');
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';  // Hide loading
        console.error('Error:', error);
        displayError('An unexpected error occurred. Please try again later.');
    }
});

// Function to display the scraped results
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
            <p>Price: ₹${product.price}</p>
            <p>Rating: ${product.rating}</p>
        `;

        resultsDiv.appendChild(productDiv);
    });
}

// Function to display error messages
function displayError(errorMessageText) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.innerText = `Error: ${errorMessageText}`;
    errorMessage.style.display = 'block';  // Show error message
}

// Function to setup CSV download link
function setupCSVDownload(csvContent) {
    const downloadLinkDiv = document.getElementById('download-link');
    const csvDownloadLink = document.getElementById('csv-download');

    // Create a Blob from the CSV content
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    // Set the href and download attributes for the link
    csvDownloadLink.href = url;
    csvDownloadLink.download = 'products.csv';
    csvDownloadLink.textContent = 'Download CSV';

    // Show the download link
    downloadLinkDiv.style.display = 'block';
}
