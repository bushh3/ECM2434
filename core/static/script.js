document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    if (form) {
        const submitButton = form.querySelector('.sign-btn');
        const loadingText = form.querySelector('.loading-text');
        const modal = document.querySelector('.success-modal');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            try {
                // Show loading state
                if (submitButton) submitButton.style.display = 'none';
                if (loadingText) loadingText.style.display = 'block';

                // Submit the form as HTML (traditional POST, not JSON)
                const formData = new FormData(form);
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'), // Still need CSRF token
                    },
                    body: formData // Send FormData directly (not JSON)
                });

                // Handle HTML response
                const text = await response.text();
                
                if (response.ok) {
                    // If the server returns a redirect (e.g., to login), follow it
                    if (response.redirected) {
                        window.location.href = response.url;
                    } else {
                        // Replace the current page content with the new HTML
                        document.documentElement.innerHTML = text;
                    }
                } else {
                    // Display server-rendered HTML error messages
                    document.documentElement.innerHTML = text;
                }
                
            } catch (error) {
                console.error('Error:', error);
                const errorMessage = document.querySelector('.error-message');
                if (errorMessage) {
                    errorMessage.textContent = 'Network error. Please try again.';
                    errorMessage.style.display = 'block';
                }
                if (submitButton) submitButton.style.display = 'block';
                if (loadingText) loadingText.style.display = 'none';
            }
        });
    }
});