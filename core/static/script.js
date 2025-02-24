document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    console.log('Form found:', form);
    
    if (form) {
        const submitButton = form.querySelector('.sign-btn');
        const loadingText = form.querySelector('.loading');
        const modal = document.querySelector('.success-modal');
        const errorElement = document.querySelector('.error, .error-message');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            try {
                if (errorElement) {
                    errorElement.style.display = 'none';
                }
                
                // Loading state
                if (submitButton) submitButton.style.display = 'none';
                if (loadingText) loadingText.style.display = 'block';
                
                // determine whether it is a login or a registration
                const isLoginForm = !form.querySelector('input[name="first_name"]');
                console.log('Is login form:', isLoginForm);
                
            
                const formData = new FormData(form);
                
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    credentials: 'include',
                    body: formData
                });
                
                // get text response
                const responseText = await response.text();
                console.log('Response status:', response.status);
                console.log('Response URL:', response.url);
                console.log('Response contains error_message:', responseText.includes('error_message'));
                console.log('Response contains Invalid details:', responseText.includes('Invalid details'));
                
               // Check the redirect URL and response content
               // If it redirects to the login page or the response contains an error message, the login has failed
                const loginFailedByUrl = response.url.includes('/login/');
                const loginFailedByContent = responseText.includes('error_message') || 
                                          responseText.includes('form.errors') || 
                                          responseText.includes('Invalid details');
                
                if (loginFailedByContent || (isLoginForm && loginFailedByUrl)) {
                    console.log('Login failed, detected by content or URL check');
                    
                    // Try to extract error messages from the response.
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = responseText;
                    const errorMsg = tempDiv.querySelector('.error, .error-message');
                    
                    if (errorMsg && errorElement) {
                        
                        errorElement.innerHTML = errorMsg.innerHTML;
                    } else if (errorElement) {
                        
                        errorElement.innerHTML = 'Invalid username or password';
                        if (isLoginForm) {
                            errorElement.innerHTML += '<p>Forgotten your password? <a href="/password_reset/">Reset password</a></p>';
                        }
                    }
                    
                    if (errorElement) {
                        errorElement.style.display = 'block';
                    }
                    
                    
                    if (submitButton) submitButton.style.display = 'block';
                    if (loadingText) loadingText.style.display = 'none';
                    
                    return; 
                }
                
                // success
                console.log('Login successful');
                
                // Show success popup
                if (modal) {
                    modal.style.display = 'flex';
                    const modalLoading = modal.querySelector('.modal-loading');
                    const modalSuccess = modal.querySelector('.modal-success');
                    
                    if (modalLoading) modalLoading.style.display = 'block';
                    if (modalSuccess) modalSuccess.style.display = 'none';
                    
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    if (modalLoading) modalLoading.style.display = 'none';
                    if (modalSuccess) modalSuccess.style.display = 'block';
                }
                
               
                if (isLoginForm) {
                    window.location.href = '/';  
                } else {
                   
                    setTimeout(() => {
                        window.location.href = '/login/';
                    }, 3000);
                }
                
            } catch (error) {
                console.error('Error:', error);
                
                // show error message
                if (errorElement) {
                    errorElement.textContent = 'Server error, please try again later';
                    errorElement.style.display = 'block';
                }
                
                if (modal) modal.style.display = 'none';
                
                
                if (submitButton) submitButton.style.display = 'block';
                if (loadingText) loadingText.style.display = 'none';
            }
        });
    }
});

// get CSRF Token function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}