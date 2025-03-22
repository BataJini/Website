document.addEventListener('DOMContentLoaded', function() {
    // Login form handler
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Here you would typically make an API call to your backend
            // For now, we'll just simulate a successful login
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userEmail', email);
            
            // Redirect to homepage after login
            window.location.href = '/index.html';
        });
    }

    // Signup form handler
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const terms = signupForm.querySelector('input[name="terms"]').checked;
            
            // Validate form
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            if (!terms) {
                alert('Please agree to the Terms & Conditions');
                return;
            }
            
            // Here you would typically make an API call to your backend
            // For now, we'll just simulate a successful registration
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userName', fullName);
            
            // Redirect to homepage after signup
            window.location.href = '/index.html';
        });
    }
});

// Check login status and update UI
function updateAuthUI() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const authButtons = document.querySelector('.header__auth');
    
    if (authButtons) {
        if (isLoggedIn) {
            const userEmail = localStorage.getItem('userEmail');
            authButtons.innerHTML = `
                <span class="user-email">${userEmail}</span>
                <button onclick="logout()" class="auth-button">Logout</button>
            `;
        } else {
            authButtons.innerHTML = `
                <a href="login.html" class="auth-button">Log In</a>
                <a href="signup.html" class="auth-button auth-button--primary">Sign Up</a>
            `;
        }
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    window.location.reload();
}

// Call updateAuthUI when the page loads
document.addEventListener('DOMContentLoaded', updateAuthUI); 