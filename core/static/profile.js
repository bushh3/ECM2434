function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function goBack() {
    window.history.back();
}


// Avatar
function uploadAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
        showPopup("Please select an image file.");
        return;
    }
    
    const formData = new FormData();
    formData.append('avatar', file);
    const csrfToken = getCookie('csrftoken');
    
    // Call the backend interface to upload the avatar, and the frontend backend connection may here----------!!!!!
    // ------------------------------------------------------------------------------前后端连接大概在这里
    fetch('/api/user/avatar', {
        method: 'POST',
        headers: {
            "X-CSRFToken": csrfToken
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const newAvatarUrl = data.avatar_url ? data.avatar_url : "/media/avatars/fox.jpg";
            document.getElementById('current-avatar').src = newAvatarUrl;
            document.getElementById("modal-avatar").src = newAvatarUrl;
            closeModal();
            showPopup("Avatar updated successfully.");
        } else {
            closeModal();
            showPopup("Avatar update failed, please try again.");
        }
    })
    .catch(err => {
        console.error("Error updating avatar:", err);
        closeModal();
        showPopup("Avatar update error, please try again later.");
    });
}
// ---------------------------------------------------------------------------------------


// update avatar - popup window  更换头像-弹窗
function openModal() {
    const currentAvatarSrc = document.getElementById("current-avatar").src;
    document.getElementById("modal-avatar").src = currentAvatarSrc;
    document.getElementById("avatar-modal").style.display = "block";
}
function closeModal() {
    document.getElementById("avatar-modal").style.display = "none";
}
var popupDuration = 3000;
function showPopup(message = "Success!") {
    const popup = document.getElementById('success-popup');
    const content = popup.querySelector('.success-popup-content');
    content.textContent = message;
    popup.style.display = 'flex';
    setTimeout(function() {
        popup.style.display = 'none';
    }, popupDuration);
}


//Get username at the greeting area
// 打招呼处获取用户名------------------------------------------------------------------------------需要获取数据库用户名
window.addEventListener("DOMContentLoaded", function() {
    fetch('/api/user/profile', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch user profile');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const displayUsername = document.getElementById('display-username');
            if (displayUsername) {
                displayUsername.textContent = data.username; //更新用户名 Update the username
            }
            const avatarImg = document.getElementById('current-avatar'); //更新头像 Update the avatar
            if (avatarImg) {
                let avatarPath = data.avatar_url && data.avatar_url !== "undefined" ? data.avatar_url : "/media/avatars/fox.jpg";
                avatarImg.src = avatarPath;
            }

            document.getElementById('username').value = data.username; //填充个人信息 Fill in personal information
            document.getElementById('email').value = data.email;
            document.getElementById('firstName').value = data.first_name;
            document.getElementById('lastName').value = data.last_name;
        }
    })
    .catch(error => {
        console.error("Error fetching user profile:", error);
    });
});



// icon - edit & save----------------------------------------------------------The display and modification of personal information
// -----------------------------------------------------------------------------------------------------个人信息的显示及更改，也要后端
function toggleEdit(fieldId, btn) {
    const inputField = document.getElementById(fieldId);
    if (inputField.disabled) {
        inputField.disabled = false;
        inputField.focus();
        inputField.style.backgroundColor = "#fff";
        inputField.style.border = "2px solid #658a65";
        btn.innerHTML = `<i class="fa fa-check-square-o"></i>`;
    } else {
        inputField.disabled = true;
        inputField.style.backgroundColor = "#eee";
        inputField.style.border = "1px solid #ccc";
        const updatedValue = inputField.value;
        const csrfToken = getCookie('csrftoken');

        // 发送 PUT 请求更新用户信息
        const updatedData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            first_name: document.getElementById('firstName').value,
            last_name: document.getElementById('lastName').value
        };

        fetch('/api/user/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "X-CSRFToken": csrfToken
            },
            credentials: 'include',
            body: JSON.stringify(updatedData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showPopup("Profile updated successfully.");

                if (data.email_changed) {
                    showPopup("Email changed, please log in again.");
                    setTimeout(() => {
                        fetch('/api/logout', { method: 'POST', credentials: 'include' })
                        .then(() => {
                            window.location.href = "/login/";
                        });
                    }, 2000);
                }

            } else {
                if (data.error === "This email is already in use.") {
                    showPopup("This email is already registered. Please use another email.");
                } else {
                    showPopup("Failed to update profile.");
                }
            }
        })
        .catch(error => {
            console.error("Error updating profile:", error);
            showPopup("An error occurred. Please try again later.");
        });
        btn.innerHTML = `<i class="fa fa-pencil-square-o"></i>`;
    }
}


//set new password-----------------------------------------------------------------------------store in database
// 修改密码，重设密码的网页放这里，登录页重设密码还有问题--------------------------------------------更改密码也要存储到数据库
function changePassword() {
    showCustomConfirm(
        "Do you want to set new password? ",
        function() {
            window.location.href = "/set_new_password/";
            //Add the logic for changing passwords here, need to build a new page of set new password
            // 这里添加修改密码的逻辑，要建一新页面
        },
        function() {}
    );
}
//log out - 登出
function logout() {
    showCustomConfirm(
        "Are you sure to log out of the account? ",
        function() {
            const csrfToken = getCookie('csrftoken');

            fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.cookie = "sessionid=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                    document.cookie = "csrftoken=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                    showPopup("Logged out successfully.");
                    setTimeout(() => {
                        window.location.href = "/login/";
                    }, 1000);
                } else {
                    showPopup("Logout failed. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error logging out:", error);
                showPopup("An error occurred while logging out.");
            });
        },
        function() {}
    );
}
// delect account - 注销账号
function deleteAccount() {
    showCustomConfirm(
        "Are you sure you want to delect your account? Your account and content will be delected permanently and cannot be restored.",
        function() {
            const csrfToken = getCookie('csrftoken');
            // connect ------------------------------------------------------- connect - 连接
            fetch('/api/user/delete', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showPopup("Account cancellation successful. ");
                    setTimeout(function(){
                        window.location.href = "/login/";
                    }, 3000);
                } else {
                    showPopup("Account cancellation failed, please try again later.");
                }
            })
            .catch(err => {
                console.error("Error deleting account:", err);
                showPopup("An error occurred while logging out of the account. Please try again later.");
            });
        },
        function() {}
    );
}



// ok button 
function showCustomConfirm(message, onConfirm, onCancel) {
    const confirmModal = document.getElementById('confirm-modal');
    const confirmMessage = document.getElementById('confirm-message');
    const okBtn = document.getElementById('confirm-ok-btn');
    const cancelBtn = document.getElementById('confirm-cancel-btn');

    confirmMessage.textContent = message;
    confirmModal.style.display = 'flex';

    function handleConfirm() {
        cleanup();
        if (onConfirm) onConfirm();
    }
    function handleCancel() {
        cleanup();
        if (onCancel) onCancel();
    }
    function cleanup() {
        confirmModal.style.display = 'none';
        okBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
    }
    okBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
}
