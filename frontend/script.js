const API_URL = "/api/v1";

async function register() {
    const username = document.getElementById("register_username").value;
    const password = document.getElementById("register_password").value;
    const email = document.getElementById("register_email").value;

    const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email })
    });

    const data = await response.json();
    alert(data.message);
    if (response.status === 201) {
        login(username, password);
    }
}

async function login(username, password) {
    if (!username || !password) {
        username = document.getElementById("login_username").value;
        password = document.getElementById("login_password").value;
    }

    const response = await fetch(`${API_URL}/auth`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", data.username);
        window.location.href = "dashboard.html"; // 成功登入後跳轉
    } else {
        alert("登入失敗，請檢查帳號或密碼");
    }
}

async function addCourse() {
    const coursecode = document.getElementById("course_code").value;
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_URL}/courses`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ course_code: coursecode })
    });

    const data = await response.json();
    alert(data.message);
    loadCourses();
}

async function deleteCourse(courseId) {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_URL}/courses/${courseId}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();
    alert(data.message);
    loadCourses();
}

async function loadCourses() {
    const token = localStorage.getItem("token");

    const response = await fetch(`${API_URL}/courses`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    const data = await response.json();
    const courseList = document.getElementById("course_list");
    courseList.innerHTML = "";
    data.forEach(course => {
        const li = document.createElement("li");
        li.className = "list-group-item d-flex justify-content-between align-items-center";
        li.textContent = course.course_code;

        const deleteButton = document.createElement("button");
        deleteButton.className = "btn btn-danger btn-sm";
        deleteButton.textContent = "刪除";
        deleteButton.onclick = () => deleteCourse(course.course_code);
        li.appendChild(deleteButton);
        courseList.appendChild(li);
    });
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "index.html";
}

function checkLogin() {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    if (!token) {
        window.location.href = "index.html";
    } else {
        document.getElementById("username").textContent = `歡迎, ${username}`;
    }
}

// 若在 dashboard 頁面，則載入課程並檢查登入狀態
if (window.location.pathname.includes("dashboard.html")) {
    checkLogin();
    loadCourses();
}
