<?php
$riding_number = mysql_escape_string($_GET["riding_number"]);
if (strlen($riding_number) != 5 || !ctype_digit($riding_number)) {
    header("Location: http://anyonebutharper.net");
    die();
}
require_once 'database.php';
$result = query("SELECT * FROM ridings WHERE number = '$riding_number'");
if (mysql_num_rows($result) != 1) {
    header("Location: http://anyonebutharper.net");
    die();
}
$data = [];
while ($row = mysql_fetch_assoc($result)) {
    $riding_name = $row['name'];
    $projected_winner = strtoupper($row['projected_winner']);
    $strategic_vote = strtoupper($row['strategic_vote']);
    $confidence = intval(round(100 * $row['confidence']));
    $turnout_2011 = intval(round(100 * $row['turnout_2011']));
    $data['con'] = intval(round(100 * $row['con']));
    $data['lib'] = intval(round(100 * $row['lib']));
    $data['ndp'] = intval(round(100 * $row['ndp']));
    $data['grn'] = intval(round(100 * $row['grn']));
    $data['bq'] = intval(round(100 * $row['bq']));
    $data['oth'] = intval(round(100 * $row['oth']));
}
mysql_free_result($result);
?>
<html>
<head>
  <title>AnyoneButHarper.net - <?php echo $riding_name; ?></title>
  <meta name="description" content="Strategic voting guide for <?php echo $riding_name; ?>. Anyone but Harper!" />
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
<div class="provincetitle"><?php echo $riding_name; ?></div>
<p>
  Projected winner &mdash;
  <span class="<?php echo $projected_winner; ?>"
        style="font-weight:bold"><?php echo $projected_winner; ?></span>
  <span class="projection <?php echo $projected_winner; ?>-proj"
        style="float:none; padding:0px 10px;">
    <?php echo $confidence; ?>%</span>
</p>
<p>
  Strongest opposition candidate &mdash;
  <span class="<?php echo $strategic_vote; ?>"
        style="font-weight:bold"><?php echo $strategic_vote; ?></span>
</p>
<p>
  Voter turnout in the last election &mdash; <?php echo $turnout_2011  ?>%
</p>
<p>If the election were held today, this is the projected popular vote in
  the riding of <?php echo $riding_name; ?>, based on the latest polls.</p>
<?php
require_once 'barchart.php';
RenderBarChart($data, 200);
?>
<p></p>
<p>
  You can <a href="http://www.elections.ca/content.aspx?section=vot&dir=reg&document=index&lang=e">
  register to vote</a> online. It's fast and easy.</p>
<p>
  The projections are updated every day until election day: October 19, 2015.
  <a href="/">AnyoneButHarper.net Home</a>
</p>
<?php include 'more_info.php'; ?>
