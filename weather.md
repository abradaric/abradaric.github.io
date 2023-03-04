<link rel="stylesheet" href="style.css">
<script src="script.js"></script>
<title>Antonio</title>
* * *
### [about me](https://abradaric.me)   |   [projects](https://abradaric.me/projects)   |   weather

<div id="main">
  <p>wtf</p>
  <div id="content"></div>
</div>

<style>
  #content {
   color: 'red';
   background: 'blue';
  }
</style>

<script>
  fetch("https://wttr.in")
    .then((res) => res.text())
    .then((data) => {
      const domParser = new DOMParser();
      const dom = domParser.parseFromString(data, "text/html");
      const table = dom.getElementsByTagName("pre")[0];
      document.getElementById("content").innerText = table.innerText;
    });
</script>
