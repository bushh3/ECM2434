document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    if (form) {
        // Base URL and API paths
        const BASE_URL = 'http://127.0.0.1:8000';
        const API_PATHS = {
            login: `${BASE_URL}/api/login`,
            signup: `${BASE_URL}/api/signup`,
            users: `${BASE_URL}/api/users`
        };
        
        // Determine if it's login or signup form
        const isLoginForm = form.querySelector('input[value="sign in"]');
        const apiUrl = isLoginForm ? API_PATHS.login : API_PATHS.signup;

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading animation
            const loading = form.querySelector('.loading');
            if (loading) loading.style.display = 'block';
            
            // Collect form data
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                if (value && key !== 'remember') {
                    data[key] = value;
                }
            });

            try {
                // API Call
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    alert(result.message || 'Success!');
                    
                    // Save user info if login successful
                    if (isLoginForm && result.user) {
                        localStorage.setItem('user', JSON.stringify(result.user));
                    }
                    
                    // Page redirection
                    if (isLoginForm) {
                        window.location.href = 'dashboard.html';
                    } else {
                        window.location.href = 'login.html';
                    }
                } else {
                    throw new Error(result.message || 'Operation failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert(error.message || 'Server error, please try again later');
            } finally {
                if (loading) loading.style.display = 'none';
            }
        });
    }
});

// Function to view all users data
async function viewAllUsers() {
    try {
        const BASE_URL = 'http://127.0.0.1:8000';
        const response = await fetch(`${BASE_URL}/api/users`);
        
        const result = await response.json();
        
        if (response.ok) {
            console.table(result.data); // Display user data in console
            return result.data;
        } else {
            throw new Error(result.message || 'Failed to get user data');
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

// Get current logged-in user info
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        console.log('Current logged-in user:', user);
        return user;
    }
    return null;
}

// Logout function
function logout() {
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}