<?php

function ValidatePostalCode($pc) {
    return (strlen($pc) == 6 &&
            ctype_alpha($pc{0}) &&
            ctype_digit($pc{1}) &&
    	    ctype_alpha($pc{2}) &&
            ctype_digit($pc{3}) &&
            ctype_alpha($pc{4}) &&
            ctype_digit($pc{5}));
}

$postal_code = strtolower(mysql_escape_string($_POST["postal_code"]));
$postal_code = mysql_escape_string(str_replace(" ", "", $postal_code));
$were_cool = True;
if (ValidatePostalCode($postal_code)) {
    include 'database.php';
    $result = query("SELECT riding_number FROM postal_codes " .
                    "WHERE postal_code = '$postal_code'");
    if (mysql_num_rows($result) == 1) {
        while ($row = mysql_fetch_assoc($result)) {
	    $riding_number = $row['riding_number'];
	    header("Location: http://anyonebutharper.net/" .
	           "riding.php?riding_number=$riding_number");
	    die();
        }
    } else {
        $were_cool = False;
    }
    mysql_free_result($result);
} else {
    $were_cool = False;
}
if (!$were_cool) {
?>
<p>
  Couldn't find that postal code, sorry. Try
  <a href="http://maps.google.com">looking it up</a> or
  <a href="/">go back</a>.
</p>
<?php } ?>
