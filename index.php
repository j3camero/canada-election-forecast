<?php require_once 'database.php'; ?>
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
<div class="provincetitle">Canada Election 2015</div>
<p>If the election were held today, these are the projected seat counts
  based on data from the last election combined with the latest polls.</p>
<?php
$seat_count_by_party = [];
$max_seat_count = 1;
$result = query("SELECT projected_winner, COUNT(*) AS seat_count " .
                "FROM ridings GROUP BY projected_winner");
while ($row = mysql_fetch_assoc($result)) {
    $party = strtolower($row['projected_winner']);
    $seat_count = $row['seat_count'];
    if ($seat_count > $max_seat_count) {
        $max_seat_count = $seat_count;
    }
    $seat_count_by_party[$party] = $seat_count;
}
mysql_free_result($result);
$party_order = ["con", "lib", "ndp", "grn", "bq"];
$party_names = [
    "con" => "Conservative",
    "lib" => "Liberal",
    "ndp" => "NDP",
    "grn" => "Green",
    "bq" => "Bloc Qu&eacute;becois",
];
foreach ($party_order as $party) {
    if (array_key_exists($party, $seat_count_by_party)) {
        $seat_count = $seat_count_by_party[$party];
    } else {
        $seat_count = 0;
    }
    $party_name = $party_names[$party];
    $bar_length = $seat_count / $max_seat_count * 200;
    echo ("<div class=\"riding $party\"><span class=\"ridingname\">" .
          "$party_name</span>" .
          "<span class=\"sequence\">" .
          "<span class=\"projection barchart $party-proj\" " .
          "style=\"width: $bar_length\">&nbsp;</span>" .
          "<span class=\"estimate $party\">" .
          "$seat_count</span></span></div>\n");
}
?>
<p></p><!-- Super lazy vertical spacer. -->
<p>
  Do you want a change of government in the 2015 Canadian election?
  Vote for the strongest candidate in your riding who isn't a member
  of the current governing party. If all non-conservatives voted this way in
  an election held today, the seat counts would be:
</p>
<?php
$seat_count_by_party = [];
$max_seat_count = 1;
$result = query("SELECT winner, COUNT(*) AS seat_count FROM " .
                "(SELECT CASE WHEN ndp+lib+grn+bq > con " .
                "THEN strategic_vote ELSE 'CON' END AS winner FROM ridings) " .
                "AS t GROUP BY winner");
while ($row = mysql_fetch_assoc($result)) {
    $party = strtolower($row['winner']);
    $seat_count = $row['seat_count'];
    if ($seat_count > $max_seat_count) {
        $max_seat_count = $seat_count;
    }
    $seat_count_by_party[$party] = $seat_count;
}
mysql_free_result($result);
foreach ($party_order as $party) {
    if (array_key_exists($party, $seat_count_by_party)) {
        $seat_count = $seat_count_by_party[$party];
    } else {
        $seat_count = 0;
    }
    $party_name = $party_names[$party];
    $bar_length = $seat_count / $max_seat_count * 200;
    echo ("<div class=\"riding $party\"><span class=\"ridingname\">" .
          "$party_name</span>" .
          "<span class=\"sequence\">" .
          "<span class=\"projection barchart $party-proj\" " .
          "style=\"width: $bar_length\">&nbsp;</span>" .
          "<span class=\"estimate $party\">" .
          "$seat_count</span></span></div>\n");
}
?>
<div class="footnote">Projections updated Sept 14, 2015</div>
<div class="provincetitle">Strategic Vote Lookup for All 338 Federal Ridings
</div>
<p>
  For your convenience, the strategic vote for all 338 federal ridings is
  listed below. The strategic vote is
  <span class="strategic">underlined</span>. The coloured boxes are the
  current  projected winners. Visit
  <a href="http://www.elections.ca/scripts/vis/FindED?L=e&PAGEID=20">
  Elections Canada</a> to look up which riding you're in.
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
$previous_province = "";
$result = query("SELECT * FROM ridings ORDER BY province, name");
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
