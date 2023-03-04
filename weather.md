<link rel="stylesheet" href="style.css">

<script src="script.js"></script>
<title>Antonio</title>
* * *
### [about me](https://abradaric.me)   |   [projects](https://abradaric.me/projects)   |   weather

<div id="content"></div>

<style>
  #content {
   display: 'block';
   box-sizing: 'content-box'
   float: 'none'
   line-height: 'normal'
   position: 'static'
   z-index: 'auto'
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
