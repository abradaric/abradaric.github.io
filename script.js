const hour = new Date().getHours();
document.getElementById("greeting").innerText = hour >= 6 && hour < 18 ? "Bonjour 👋" : "Bonsoir 👋";
