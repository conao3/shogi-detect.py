<html>
  <head>
    <meta charset="utf-8">

    <style type="text/css">
      img {
	  margin:-2pt;
      }
    </style>
    <script type="text/javascript">
      window.onload = function onLoad () {
	  var images = document.querySelectorAll('img');
	  images.forEach(function(image) {
	      image.addEventListener("click", function() {
		  // クリックされたらstyle属性を直接書き換える
		  image.style.opacity = '0.5';
	      }, false);

	      
	      image.addEventListener("dblclick", function() {
		  // ダブルクリックされたらstyle属性を除去
		  image.removeAttribute("style");
	      }, false);

	  });
      }
      
      function show () {
	  var images = document.querySelectorAll('img');
	  message = "mv ";
	  images.forEach(function(image) {
	      if (image.getAttribute("style")) {
		  message = message + "\"" + image.getAttribute("src") + "\" ";
	      }
	  });

	  message = message + "_p/"
	  showplace = document.getElementById("selectplace");
	  showplace.innerHTML = message;
      }
    </script>
  </head>
  <body style="background-color:#1C1414; color:#cae682;">
    <div id="showplace">
      <input type="button" value="表示" onClick="show()">
      <textarea id="selectplace" rows="5" cols="50"></textarea>
    </div>
    <div id="imgplace">
      <?php showimg() ?>
    </div>
    <!-- <?php phpinfo() ?> -->
    <br />
  </body>
</html>

<?php
 function showimg() {
 $filepaths = glob('./piecies/*.png');
 $i=0;
 foreach($filepaths as $filepath) {
 $i=$i+1;
 echo "<img width=\"66\", height=\"66\", src=", $filepath, ">";
echo("\n");
}
}
