document.getElementById("greeting").innerText =
  new Date().getHours() >= 18 ? "Bonsoir 👋" : "Bonjour 👋";

function loadScript(src, dataDomain) {
  // Check if script is already loaded based on 'src' and 'data-domain'
  var existingScript = document.querySelector(`script[src="${src}"][data-domain="${dataDomain}"]`);
  if (existingScript) {
    return; // Script is already loaded
  }

  var script = document.createElement("script");
  script.src = src;
  script.defer = true;
  script.setAttribute("data-domain", dataDomain);
  document.head.appendChild(script);
}

loadScript("https://plausible.io/js/script.js", "abradaric.me");
