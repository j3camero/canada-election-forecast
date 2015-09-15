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
<div class="provincetitle">Strategic Vote Lookup for All 338 Federal Ridings
</div>
<p>
  Do you want a change of government in the 2015 Canadian election?
  Vote for the strongest candidate in your riding who isn't a member
  of the current governing party.
</p>
<p>
  For your convenience, the strategic vote for all 338 federal ridings is
  listed below. The strategic vote is
  <span class="strategic">underlined</span>. The coloured boxes are the
  current  projected winners. Visit
  <a href="http://www.elections.ca/scripts/vis/FindED?L=e&PAGEID=20">
  Elections Canada</a> to look up which riding you're in.
</p>
<div class="footnote">Projections updated Sept 14, 2015</div>
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
    $projected_winner = strtolower($row['projected_winner']);
    $strategic_vote = strtolower($row['strategic_vote']);
    $confidence = intval(round(100 * $row['confidence']));
    if ($province != $previous_province) {
        if ($previous_province != "") {
            echo ("<div class=\"footnote\">Strategic vote is " .
                  "<span class=\"strategic\">underlined</span>." .
                  "The coloured box is the current projected " .
                  "winner.</div>\n");
        }
	$province_name = $province_names[$province];
        echo "<div class=\"provincetitle\">$province_name</div>\n";
    }
    $previous_province = $province;
    echo "<div class=\"riding\"><span class=\"ridingname\">$name</span>";
    echo "<span class=\"sequence\">";
    foreach ($party_order as $party) {
        if ($party == "bq" && $province != "QC") {
	    continue;
        }
        $support = intval(round(100 * $row[$party]));
	$extra_classes = "";
	if ($party == $strategic_vote) {
	    $extra_classes .= " strategic";
        }
	echo "<span class=\"estimate $party $extra_classes\">$support</span>";
    }
    echo ("<span class=\"projection $projected_winner-proj\">" .
          "$confidence%</span></span></div>\n");
}
mysql_free_result($result);
mysql_close();
?>
</body>
</html>
