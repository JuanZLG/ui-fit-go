
<?php

session_start();
session_destroy();

mysqli_close($conectar);
header('location:../login.php');
exit();

?>