<html>
<head>
  <title>AnyoneButHarper.net</title>
  <meta charset="ISO-8859-1">
  <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-67491457-1', 'auto');
  ga('send', 'pageview');

</script>
<?php
require_once 'database.php';
$province_names = [
    "AB" => "Alberta",
    "BC" => "British Columbia",
    "MB" => "Manitoba",
    "NB" => "New Brunswick",
    "NL" => "Newfoundland &amp; Labrador",
    "NS" => "Nova Scotia",
    "NT" => "Northwest Territories",
    "NU" => "Nunavut",
    "ON" => "Ontario",
    "PE" => "Prince Edward Island",
    "QC" => "Qu&eacute;bec",
    "SK" => "Saskatchewan",
    "YT" => "Yukon",
];
$party_order = ["con", "lib", "ndp", "grn", "bq"];
$previous_province = "";
while ($row = mysql_fetch_assoc($result)) {
    $province = $row["province"];
    $name = $row["name"];
    if ($province != $previous_province) {
	$province_name = $province_names[$province];
        echo "<h2>$province_name</h2>\n";
    }
    $previous_province = $province;
    echo "<div class=\"riding\"><span class=\"ridingname\">$name</span>";
    echo "<span class=\"sequence\">";
    foreach ($party_order as $party) {
        if ($party == "bq" && $province != "QC") {
	    continue;
        }
        $support = intval(round(100 * $row[$party]));
	echo "<span class=\"estimate $party\">$support</span>";
    }
    echo "</span></div>\n";
}
mysql_free_result($result);
mysql_close();
?>
</body>
</html>
