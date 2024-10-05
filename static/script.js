// script.js

document.getElementById('scrape-form').addEventListener('submit', async function(event) {
    event.preventDefault();  // Prevent page refresh

    const url = document.getElementById('url').value;

    try {
        // Send POST request to backend with the URL
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        // Get the scraped data
        const data = await response.json();

        if (response.ok) {
            displayResults(data.products);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// Display the results on the page
function displayResults(products) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

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
