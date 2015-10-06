<?php

include 'database.php';

function ValidatePostalCode($pc) {
    return (strlen($pc) == 6 &&
            ctype_alpha($pc{0}) &&
            ctype_digit($pc{1}) &&
    	    ctype_alpha($pc{2}) &&
            ctype_digit($pc{3}) &&
            ctype_alpha($pc{4}) &&
            ctype_digit($pc{5}));
}

function ValidateRidingNumber($riding_number) {
    return strlen($riding_number) == 5 && ctype_digit($riding_number);
}

function ElectionsCanadaPostalCodeLookup($postal_code) {
    $url = 'http://www.elections.ca/Scripts/vis/FindED?L=e&QID=-1&PAGEID=20';
    $data = array('CommonSearchTxt' => $postal_code, 'CivicSearchTxt' => '1');
    $options = array(
        'http' => array(
            'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
            'method'  => 'POST',
            'content' => http_build_query($data),
        ),
    );
    $context  = stream_context_create($options);
    $html = file_get_contents($url, false, $context);
    $pattern_matches = [];
    preg_match_all("/ED=\d{5}/", $html, $pattern_matches);
    if (count($pattern_matches) == 0) {
         return NULL;
    }
    if (count($pattern_matches[0]) == 0) {
        return NULL;
    }
    return substr($pattern_matches[0][0], 3);
}

function DatabaseThenElectionsCanadaThenAvaaz($postal_code) {
    if (!ValidatePostalCode($postal_code)) {
        return NULL;
    }
    $result = query("SELECT * FROM postal_codes " .
                    "WHERE postal_code = '$postal_code'");
    if (mysql_num_rows($result) != 1) {
        mysql_free_result($result);
        return NULL;
    }
    $row = mysql_fetch_assoc($result);
    $avaaz_riding_number = $row['avaaz_riding_number'];
    $ec_riding_number = $row['ec_riding_number'];
    mysql_free_result($result);
    if (!is_null($ec_riding_number)) {
        return $ec_riding_number;
    }
    $ec_riding_number = mysql_escape_string(
                            ElectionsCanadaPostalCodeLookup($postal_code));
    if (is_null($ec_riding_number)) {
        return $avaaz_riding_number;
    }
    query("UPDATE postal_codes SET ec_riding_number = '$ec_riding_number' " .
          "WHERE postal_code = '$postal_code'");
    return $ec_riding_number;
}

$postal_code = strtolower(mysql_escape_string($_POST["postal_code"]));
$postal_code = mysql_escape_string(str_replace(" ", "", $postal_code));
$riding_number = DatabaseThenElectionsCanadaThenAvaaz($postal_code);
if (ValidateRidingNumber($riding_number)) {
    header("Location: http://anyonebutharper.net/" .
           "riding.php?riding_number=$riding_number");
    die();
} else {
?>
<p>
  Couldn't find that postal code, sorry. Try
  <a href="http://maps.google.com">looking it up</a> or
  <a href="/">go back</a>.
</p>
<?php } ?>
