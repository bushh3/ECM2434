document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    console.log('Form found:', form);
    
    if (form) {
        const submitButton = form.querySelector('.sign-btn');
        const loadingText = form.querySelector('.loading'); 
        const modal = document.querySelector('.success-modal');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');


try {
    // Loading state
    if (submitButton) submitButton.style.display = 'none';
    if (loadingText) loadingText.style.display = 'block';

    // determine login/signup
    const isLoginForm = !form.querySelector('input[name="first_name"]');
    console.log('Is login form:', isLoginForm);

 
    const formData = new FormData(form);
    
    // call API
    const response = await fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include',
        body: formData  
    });



    if (response.ok) {
        // Show popup 
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

        // handle redirection
        if (isLoginForm) {
            window.location.href = '/'; 
        } else {
            setTimeout(() => {
                window.location.href = '/login/';
            }, 3000);
        }
    } else {
        throw new Error('Error');
    }
    

    
} catch (error) {
    console.error('Error:', error);
    const errorMessage = document.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.textContent = error.message || 'Server error, please try again later';
        errorMessage.style.display = 'block';
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

