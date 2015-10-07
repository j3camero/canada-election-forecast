<?php
require_once 'database.php';
require_once 'barchart.php';
?>
<html>
<head>
  <title>AnyoneButHarper.net</title>
  <meta name="description" content="Strategic voting guide for the 2015 Canadian federal election. Anyone but Harper!" />
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
<div class="provincetitle">Canada Election 2015</div>
<p>If the election were held today, these are the projected seat counts
  based on the latest polls.</p>
<?php
SqlBarChart("SELECT projected_winner, COUNT(*) AS seat_count " .
            "FROM ridings GROUP BY projected_winner", 200);
?>
<p></p><!-- Super lazy vertical spacer. -->
<p>
  Do you want a change of government in the 2015 Canadian election?
  Vote for the strongest candidate in your riding who isn't a member
  of the current governing party. If all non-conservatives voted this way,
  the seat counts would be:
</p>
<?php
SqlBarChart("SELECT winner, COUNT(*) AS seat_count FROM " .
            "(SELECT CASE WHEN ndp+lib+grn+bq+oth > con " .
            "THEN strategic_vote ELSE 'CON' END AS winner FROM ridings) " .
            "AS t GROUP BY winner", 200);
?>
<p></p><!-- Super lazy vertical spacer. -->
<p>
  You can <a href="http://www.elections.ca/content.aspx?section=vot&dir=reg&document=index&lang=e">
  register to vote</a> online. It's fast and easy.</p>
<div class="footnote">Projections updated Oct 7, 2015</div>
<div class="provincetitle">Strategic Vote Lookup for All 338 Federal Ridings
</div>
<p>Visit Elections Canada to
  <a href="http://www.elections.ca/scripts/vis/FindED?L=e&PAGEID=20">
  look up your riding</a> or enter your postal code here:
</p>
<form action="postal_code_lookup.php" method="post"><p>
    <input type="text" name="postal_code" size="8" id="postal_code">
    <input type="submit" value="Go!" id="submit_button">
</p></form>
<p>
  The strongest opposition candidate is
  <span style="text-decoration:underline">underlined</span>. The coloured
  boxes are the current projected winners.
</p>
<?php
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
$party_order = ["con", "lib", "ndp", "grn", "bq", "oth"];
$previous_province = "";
$result = query("SELECT * FROM ridings ORDER BY province, name");
while ($row = mysql_fetch_assoc($result)) {
    $province = $row["province"];
    $name = $row["name"];
    $riding_number = $row["number"];
    $projected_winner = strtolower($row['projected_winner']);
    $strategic_vote = strtolower($row['strategic_vote']);
    $confidence = intval(round(100 * $row['confidence']));
    if ($province != $previous_province) {
        if ($previous_province != "") {
            echo ("<div class=\"footnote\">Strongest opposition candidate " .
                  "is <span style=\"text-decoration:underline\">" .
                  "underlined</span>." .
                  "The coloured box is the current projected " .
                  "winner.</div>\n");
        }
	$province_name = $province_names[$province];
        echo "<div class=\"provincetitle\">$province_name</div>\n";
    }
    $previous_province = $province;
    echo "<div class=\"riding\">\n";
    echo ("<a href=\"riding.php?riding_number=$riding_number\" " .
          "class=\"ridingname\">$name</a>\n");
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
include 'more_info.php';
?>
