<?php require_once 'database.php'; ?>
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
require_once 'barchart.php';
RenderBarChart($seat_count_by_party, 200);
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
RenderBarChart($seat_count_by_party, 200);
?>
<p></p><!-- Super lazy vertical spacer. -->
<p>
  You can <a href="http://www.elections.ca/content.aspx?section=vot&dir=reg&document=index&lang=e">
  register to vote</a> online. It's fast and easy.</p>
<div class="footnote">Projections updated Sept 16, 2015</div>
<div class="provincetitle">Strategic Vote Lookup for All 338 Federal Ridings
</div>
<p>
  For your convenience, the strategic vote for all 338 federal ridings is
  listed below. The strategic vote is
  <span style="text-decoration:underline">underlined</span>. The coloured
  boxes are the current  projected winners. Visit
  <a href="http://www.elections.ca/scripts/vis/FindED?L=e&PAGEID=20">
  Elections Canada to look up which riding</a> you're in.
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
$party_order = ["con", "lib", "ndp", "grn", "bq"];
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
                  "<span style=\"text-decoration:underline\">" .
                  "underlined</span>." .
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
<div class="provincetitle">More Info</div>
<p>
  More information about
  <a href="https://en.wikipedia.org/wiki/Tactical_voting">
  strategic voting</a>.
</p>
<p>
  All projections and strategic voting recommendations displayed on this page
  are calculated by an impartial algorithm.
  <a href="https://github.com/j3camero/canada-election-forecast">
  The code is on GitHub</a>. You can download and run it on your own
  computer if you like. The model forecasts the popular vote in all 338
  federal ridings by starting with the 2011 election results and
  applying an adjustment calculated from the latest regional polling data.
</p>
<p>
  Election forecasting is not an exact science. Many of the riding projections
  listed on this page will turn out to be wrong. The data is provided
  under the philosophy that an educated guess is better than no
  information at all.
</p>
<div class="footnote">Projections updated Sept 16, 2015</div>
</body>
</html>
