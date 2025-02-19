document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    console.log('Form found:', form);
    
    if (form) {
        const submitButton = form.querySelector('.sign-btn');
        const loadingText = form.querySelector('.loading');  // 修改为 .loading
        const modal = document.querySelector('.success-modal');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted');
 
// //TEST
//             try {
//                 // 只显示按钮的loading
//                 if (submitButton) submitButton.style.display = 'none';
//                 if (loadingText) loadingText.style.display = 'block';
                
//                 // 显示弹窗
//                 if (modal) {
//                     modal.style.display = 'flex';
//                     const modalLoading = modal.querySelector('.modal-loading');
//                     const modalSuccess = modal.querySelector('.modal-success');
                    
//                     if (modalLoading) modalLoading.style.display = 'block';
//                     if (modalSuccess) modalSuccess.style.display = 'none';
                    
//                     await new Promise(resolve => setTimeout(resolve, 2000));
                    
//                     if (modalLoading) modalLoading.style.display = 'none';
//                     if (modalSuccess) modalSuccess.style.display = 'block';
//                 }
                
//             } catch (error) {
//                 console.error('Error:', error);
//                 if (modal) modal.style.display = 'none';
//                 if (submitButton) submitButton.style.display = 'block';
//                 if (loadingText) loadingText.style.display = 'none';
//                 alert('An error occurred. Please try again.');
//             }
//         });
//     }
// });

try {
    // Loading state
    if (submitButton) submitButton.style.display = 'none';
    if (loadingText) loadingText.style.display = 'block';

    // 判断是登录还是注册表单
    const isLoginForm = !form.querySelector('input[name="first_name"]');
    console.log('Is login form:', isLoginForm);

    // 直接使用表单数据
    const formData = new FormData(form);
    
    // 调用API
    const response = await fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include',
        body: formData  // 直接使用 FormData
    });



    if (response.ok) {
        // Show popup 显示弹窗
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

        // 根据表单类型处理重定向
        if (isLoginForm) {
            window.location.href = '/';  // 登录成功后跳转到首页
        } else {
            // 注册成功后等待3秒然后跳转到登录页
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

