
<?php

require 'conectar.php';

session_start();

$correo = $_POST['correo'];
$clave = $_POST['pw'];

$username = "SELECT Nombres from usuarios";
$nombreUsu = mysqli_query($conectar, $username);

$q = "SELECT COUNT (*) as contar from usuarios where Email = '$correo' and contra = '$clave'";

$consulta = mysqli_query($conectar, $q);
$arrayDTO = mysqli_fetch_array($consulta);

if($arrayDTO['contar']>0){
    header("location: ../index.php");
} else {
    echo "<h6>Datos Incorrectos</h6>";
}

?>