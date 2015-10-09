<?php
$group_name = mysql_escape_string($_GET["group_name"]);
?>
<html>
<head>
  <title>AnyoneButHarper.net - <?php echo $group_name; ?></title>
  <meta name="description" content="Strategic voting guide for <?php echo $group_name; ?>. Anyone but Harper!" />
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
<div class="provincetitle">Canada Election 2015 &mdash;
  <?php echo $group_name; ?></div>
<p>Back to <a href="/">AnyoneButHarper.net</a> home.</p>
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
$party_order = ["con", "lib", "ndp", "grn", "bq", "oth"];
require_once 'database.php';
$result = query("SELECT ridings.* " .
                "FROM riding_groups INNER JOIN ridings " .
                "ON riding_groups.riding_number = ridings.number " .
                "WHERE group_name = '$group_name' ORDER BY name");
while ($row = mysql_fetch_assoc($result)) {
    $province = $row["province"];
    $name = $row["name"];
    $riding_number = $row["number"];
    $projected_winner = strtolower($row['projected_winner']);
    $strategic_vote = strtolower($row['strategic_vote']);
    $confidence = intval(round(100 * $row['confidence']));
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
?>
<p></p><!-- Super lazy vertical spacer. -->
<p>Back to <a href="/">AnyoneButHarper.net</a> home.</p>
<?php include 'more_info.php'; ?>
