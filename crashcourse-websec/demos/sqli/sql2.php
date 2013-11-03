<?php
function random($len) {
	$file = fopen('/dev/urandom', 'r');
	$urandom = fread($file, $len);
	fclose($file);

	$ret = '';
	for ($i=0; $i<$len; $i++) 
		$ret .= dechex(ord($urandom[$i]));

	return $ret;
}

if(!$db = @mysql_connect('localhost', 'sql2', 'sql2')) {
  die($error_mysql);
}
if(!@mysql_select_db('sql2', $db)) {
  die($error_mysql);
}

if ($_GET['action'] == 'upload') {
  $allowed = array('gif', 'jpeg', 'jpg', 'png');
  $tmp = explode(".", $_FILES['prove']['name']);
  $ext = end($tmp);
  $name = basename($_FILES['prove']['name']);
  $filename = random(16).".".$ext;
  if (!isset($_POST['rating']) || empty($_POST['rating']))
    die("You must supply a rating");
  if (!isset($_POST['title']) || empty($_POST['title']))
    die("You must supply a title");

  $rating = mysql_real_escape_string($_POST['rating']);
  $title = mysql_real_escape_string($_POST['title']);
  $prove = "";

  if (intval($rating) < 1 || intval($rating) > 3)
    $rating = 1;

  if ($_FILES['prove']['size'] > 0) {
    if ($_FILES['prove']['size'] < 100000 && in_array($ext, $allowed)) {
      move_uploaded_file($_FILES['prove']['tmp_name'], "upload/".$filename);
      $prove = "upload/".$filename;
    } else {
      if (!in_array($ext, $allowed))
        die("File extension not allowed");
      else
        die("The file is larger than 100 kB");
    }
  }

  $prove = mysql_real_escape_string($prove);

  $data = array(
    'rating' => $rating,
    'title' => "'$title'",
    'prove' => "'$prove'",
    'approved' => 1
  );

  mysql_db_query('sql2', "INSERT INTO bugs (rating, title, prove) VALUES ($rating, '$title', '$prove');") or die (mysql_error());
  die("Bug successfully included! Can be downloaded at <a href='/sql2.php?action=dl&id=" . mysql_insert_id() . "'>this link</a>");
} else {
  $id = isset($_GET['id']) ? intval($_GET['id']) : -1;
  $result = mysql_db_query('sql2', "SELECT prove FROM bugs WHERE id=$id LIMIT 1") or die(mysql_error());
  $data = mysql_fetch_row($result);
  $file = "./".$data[0];

  if (substr_count($file, "../") > 0)
    die('No need to go back :), nothing of interest for you');

  if (file_exists($file)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename='.basename($file));
    header('Content-Transfer-Encoding: binary');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($file));
    ob_clean();
    flush();
    readfile($file);
    die();
  } else {
    die("File $file doesn't exist");
  }
  die("Success!");
}
?>

