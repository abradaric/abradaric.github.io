<link rel="stylesheet" href="style.css">
<script src="script.js"></script>
<title>Antonio</title>
* * *
### [about me](https://abradaric.me)   |   [projects](https://abradaric.me/projects)   |   weather

<pre id="box">Loading...</pre>
<br/>
<small><3 @wttr.in API</small>
<div style="height: 0px">U2FsdGVkX19QVgz3ZcqA1PnGva1Pig10CybthmTYoHS8lWQ78BJpeyG1LM9UxFQFBMOrWeJ0UoN2T37gVawAeA== #(aes256cbc)</div>

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
