// auth.js - 用户认证和登录状态管理

// API 基础 URL
const API_BASE_URL = '';

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

        const response = await fetch(`${API_BASE_URL}/api/users/profile`, {
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
        const response = await fetch(`${API_BASE_URL}/api/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            setToken(data.access_token);
            return { success: true };
        } else {
            return {
                success: false,
                message: '登录失败，请检查邮箱和密码'
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

// 退出登录
function logout() {
    clearToken();
    // 可以在这里添加其他退出登录时需要执行的操作
}

// 更新UI以反映登录状态
async function updateAuthUI() {
    const isLoggedIn = isAuthenticated();
    const loginSection = document.getElementById('login-section');
    const userInfoSection = document.getElementById('user-info');

    if (!loginSection || !userInfoSection) {
        return; // 页面上可能没有这些元素
    }

    if (isLoggedIn) {
        loginSection.style.display = 'none';
        userInfoSection.style.display = 'block';

        const userProfile = await fetchUserProfile();
        if (userProfile) {
            const usernameElement = document.getElementById('username');
            const pointsBalanceElement = document.getElementById('points-balance');

            if (usernameElement) {
                usernameElement.textContent = userProfile.username;
            }

            if (pointsBalanceElement) {
                pointsBalanceElement.textContent = userProfile.points_balance;
            }
        }
    } else {
        if (loginSection) loginSection.style.display = 'block';
        if (userInfoSection) userInfoSection.style.display = 'none';
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