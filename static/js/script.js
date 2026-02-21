// ================= FLASH MESSAGE AUTO HIDE =================
setTimeout(() => {
    const alert = document.querySelector('.alert');
    if(alert){
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
    }
}, 3000);


// ================= THEME SYSTEM =================
const toggleBtn = document.getElementById("themeToggle");
const icon = document.getElementById("themeIcon");

// Load saved theme on every page
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");

    if(savedTheme === "dark"){
        document.body.classList.add("dark");
        icon.textContent = "☀️";
    } else {
        icon.textContent = "🌙";
    }
});

toggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    if(document.body.classList.contains("dark")){
        localStorage.setItem("theme", "dark");
        icon.textContent = "☀️";
    } else {
        localStorage.setItem("theme", "light");
        icon.textContent = "🌙";
    }
});


// ================= DELETE MODAL =================
function confirmDelete(id){
    const modal = document.getElementById("modal");
    const form = document.getElementById("deleteForm");
    form.action = "/delete/" + id;
    modal.style.display = "flex";
}

function closeModal(){
    document.getElementById("modal").style.display = "none";
}