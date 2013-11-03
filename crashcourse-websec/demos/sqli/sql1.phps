<?php
 
$key = "union_makes_force";

$login = $_POST['login'];
$password = $_POST['password'];

if(!$db = @mysql_connect('localhost', 'sql1', 'sql1')) {
  die($error_mysql);
}
if(!@mysql_select_db('sql1', $db)) {
  die($error_mysql);
}

$result = mysql_db_query('sql1', "SELECT pass FROM users WHERE user='$login'") or die (mysql_error());
$num_rows = mysql_num_rows($result);
$row = mysql_fetch_row($result);

if (($num_rows != 0) && (!strcasecmp(md5($password), $row[0]))) {
  die("Authentication successful! The key is " . $key);
} else {
  die("Authentication unsuccessful!");
}

?>
