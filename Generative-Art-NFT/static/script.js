document.getElementById('envForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(document.getElementById('envForm'));

    fetch('/set_env', {
        method: 'POST',
        body: formData
    })
    .then(response => 
        response.json()
    ).then(data => {
        if (data.error) {
            alert(data.error);
            
        }
        else {
            document.getElementById('envForm').style.display = 'none';
            document.getElementById('imageForm').style.display = 'inline';
            document.getElementById('cleanButton').style.display = 'inline';
            document.getElementsByClassName('warning')[0].style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred. Please try again.")
});
});

document.getElementById('imageForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(document.getElementById('imageForm'));

    // Show the loader
    document.getElementById('loader').style.display = 'block';
    document.getElementById('resultContainer').innerHTML = ''; // Clear previous results
    document.getElementById('generateButton').style.display = 'none'; // Hide generate button
    document.getElementById('cleanButton').style.display = 'none'; // Hide clean button
    document.getElementById('cleanEnvButton').style.display = 'none';
    document.getElementById('imageForm').style.display = 'none'; 
    fetch('/generate', {
        method: 'POST',
        body: formData
    })
    .then(response => 
        response.json()
    ).then(data => {
        if (data.error) {
            alert(data.error);
            document.getElementById('generateButton').style.display = 'inline'; // Show generate button
            document.getElementById('cleanButton').style.display = 'inline'; // Show clean button
            document.getElementById('imageForm').style.display = 'inline'; 
        }
        else {
            // Hide the loader
            document.getElementById('loader').style.display = 'none';

            // Create an image element for the output image
            var img = new Image();
            img.src = data.mcs_img_link;
            img.alt = 'Generated Image';
            img.style.maxWidth = '100%'; // Optional: to ensure image fits in the container

            // Clear the result container and append the image
            var resultContainer = document.getElementById('resultContainer');
            resultContainer.innerHTML = '';
            resultContainer.appendChild(img);

            // Add the hyperlinks
            var linksHtml = `
                <p style="color:white">Chainlink Function Contract Address: ${data.chain_link_fn_contract_address}</p>
                <p style="color:white">NFT Contract Address: ${data.NFT_contract_address}</p>
                <p><a style="color:white" a href="${data.dataset_address}" target="_blank">Dataset Link</a></p>
                <p><a style="color:white" href="${data.mcs_img_link}" target="_blank">Image Link</a></p>
                <p><a style="color:white" href="https://mumbai.polygonscan.com/tx/${data.license_mint_hash}" target="_blank">Transaction Link</a></p>
                <p><a style="color:white" href="${data.NFT_collection}" target="_blank">OpenSea Marketplace</a></p>
            `;

            resultContainer.innerHTML += linksHtml;
            document.getElementById('main_title').style.display = 'none';
            document.getElementById('cleanButton').style.display = 'inline'; // Show clean button
        }
    }).catch((error) => {
        console.error('Error:', error);
        document.getElementById('imageForm').style.display = 'inline'; 
        alert("An error occurred. Please try again.")

    }).finally(() => {
        document.getElementById('loader').style.display = 'none';
        document.getElementById('generateButton').style.display = 'inline'; // Show generate button
        document.getElementById('cleanButton').style.display = 'inline'; // Show clean button
        document.getElementById('cleanEnvButton').style.display = 'inline';
    });
});
function cleanResults() {
    // Clear the result container
    document.getElementById('resultContainer').innerHTML = '';

    // Optionally, reset the form fields
    document.getElementById('imageForm').reset();
    
    // Hide the loader and the abort button if they are visible

    document.getElementById('generateButton').style.display = 'inline'; // Show generate button
    document.getElementById('main_title').style.display = 'inline';
    document.getElementById('imageForm').style.display = 'inline'; 
    
};
function cleanEnv() {
    document.getElementById('resultContainer').innerHTML = '';

    document.getElementById('envForm').reset();

    document.getElementById('envForm').style.display = 'inline';
    document.getElementById('imageForm').style.display = 'none'; 
    document.getElementById('cleanButton').style.display = 'none';
    document.getElementById('main_title').style.display = 'inline';
    document.getElementsByClassName('warning')[0].style.display = 'inline';
}