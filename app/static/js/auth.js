// auth.js - 用户认证和登录状态管理

// API 基础 URL
if (typeof API_BASE_URL === 'undefined') {
    var API_BASE_URL = '/api';
}

// 获取存储的令牌
function getToken() {
    return localStorage.getItem('token');
}

// 设置令牌
function setToken(token) {
    localStorage.setItem('token', token);
}

// 清除令牌
function clearToken() {
    localStorage.removeItem('token');
}

// 检查用户是否已登录
function isAuthenticated() {
    return !!getToken();
}

// 获取用户信息
async function fetchUserProfile() {
    try {
        const token = getToken();
        if (!token) {
            return null;
        }

        const response = await fetch(`${API_BASE_URL}/users/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            return await response.json();
        } else {
            // Token 可能已过期
            clearToken();
            return null;
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
        return null;
    }
}

// 登录函数
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            return { success: true, user: data.user };
        } else {
            const errorData = await response.json();
            return {
                success: false,
                message: errorData.error || '登录失败，请检查邮箱和密码'
            };
        }
    } catch (error) {
        console.error('登录请求失败:', error);
        return {
            success: false,
            message: '登录请求失败，请稍后再试'
        };
    }
}

// 获取当前用户信息
function getCurrentUser() {
    const userString = localStorage.getItem('user');
    return userString ? JSON.parse(userString) : null;
}

// 更新用户信息
function updateCurrentUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

// 退出登录
function logout() {
    clearToken();
    localStorage.removeItem('user');
    // 可以在这里添加其他退出登录时需要执行的操作
}

// 更新UI以反映登录状态
async function updateAuthUI() {
    const isLoggedIn = isAuthenticated();
    const guestContent = document.getElementById('guest-content');
    const userContent = document.getElementById('user-content');

    if (!guestContent || !userContent) {
        return; // 页面上可能没有这些元素
    }

    if (isLoggedIn) {
        guestContent.style.display = 'none';
        userContent.style.display = 'block';

        const user = getCurrentUser();
        if (user) {
            const usernameElement = document.getElementById('username-display');
            const pointsBalanceElement = document.getElementById('points-display');

            if (usernameElement) {
                usernameElement.textContent = user.username;
            }

            if (pointsBalanceElement) {
                pointsBalanceElement.textContent = user.points_balance;
            }
        } else {
            // 如果本地没有用户信息，尝试从服务器获取
            const userProfile = await fetchUserProfile();
            if (userProfile) {
                updateCurrentUser(userProfile);
                updateAuthUI(); // 递归调用以更新UI
            }
        }
    } else {
        guestContent.style.display = 'block';
        userContent.style.display = 'none';
    }
}

// 检查受保护页面的访问权限
function checkProtectedPage() {
    // 在需要登录才能访问的页面调用此函数
    if (!isAuthenticated()) {
        window.location.href = '/'; // 重定向到首页
        return false;
    }
    return true;
}

// 页面加载时初始化认证状态
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();

    // 绑定登出按钮事件
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            logout();
            window.location.href = '/'; // 退出登录后重定向到首页
        });
    }

    // 绑定登录表单提交事件
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const result = await login(email, password);
            if (result.success) {
                updateAuthUI();
                window.location.href = '/products'; // 登录成功后重定向到商品页面
            } else {
                alert(result.message);
            }
        });
    }
});