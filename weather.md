<link rel="stylesheet" href="style.css">
<script src="script.js"></script>
<title>Antonio</title>
* * *
### [about me](https://abradaric.me)   |   [projects](https://abradaric.me/projects)   |   weather

<pre id="box"></pre>
<br/>
<small><3 @wttr.in API</small>

<style> 
  #box {
    font-size: 11px;
  }
</style>

<script>
  fetch("https://wttr.in")
    .then((res) => res.text())
    .then((data) => {
      const domParser = new DOMParser();
      const dom = domParser.parseFromString(data, "text/html");
      const table = dom.getElementsByTagName("pre")[0];
      document.getElementById("box").innerText = table.innerText;
    });
</script>
