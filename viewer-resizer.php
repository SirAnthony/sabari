<?php
### Originaly script by Sir Anthony
#Типа лицензия MIT и все такое
$picsize="200";
function imageworks($fval){
	global $picsize;
		$imgsize=getimagesize($fval) or print "Error. Couldn't get image data.";
	switch ($imgsize['mime']) {
		case 'image/gif':
			if (imagetypes() & IMG_GIF) {
				$IMG = imagecreatefromGIF($fval) ;
			}else{
				$err_str = 'GD не поддерживает GIF';
			}
		break;
		case 'image/jpeg':
			if (imagetypes() & IMG_JPG) {
				$IMG = imagecreatefromJPEG($fval) ;
			}else{
				$err_str = 'GD не поддерживает JPEG';
			}
		break;
		case 'image/png':
			if (imagetypes() & IMG_PNG) {
				$IMG = imagecreatefromPNG($fval) ;
			}else{
				$err_str = 'GD не поддерживает PNG';
			}
		break;
		default:
			$err_str = 'GD не поддерживает ' . $image_info['mime'];
	}
	$imgwidth = imagesx($IMG) ;
	$imgheight = imagesy($IMG) ;
	if ($imgwidth < $imgheight) {
	$iheight=$picsize;
	$iwidth = round($picsize * $imgwidth / $imgheight);
	}else{
	$iwidth=$picsize;
	$iheight=round($picsize * $imgheight / $imgwidth);
	}

	$NIMG = imagecreatetruecolor($iwidth , $iheight);
	imagealphablending($NIMG, false);
	imagesavealpha($NIMG, true);
	
	imagecopyresampled($NIMG, $IMG, 0, 0, 0, 0, $iwidth, $iheight, $imgsize["0"], $imgsize["1"]);
	
	imagepng($NIMG);	
	
	imagedestroy($IMG);
	imagedestroy($NIMG);
}

if(isset($_GET["f"])){
	$cache_file_name = md5($_GET["f"]);
	$cache_mtime = 0;
	if (is_file("/cache/".$cache_file_name)) {
		$cache_mtime = filemtime("/cache/".$cache_file_name);
	}
	header('Content-Type: image/png');	
	$fmtime = filemtime($_GET["f"]);
	if ($cache_mtime < $fmtime) {
		ob_start();
		$result = imageworks($_GET["f"]);
		$thumbnail = ob_get_contents();
		$thumb_size = ob_get_length();
		ob_end_clean();
		if ($result) {
			echo 'Ошибка: '. $result;
			exit();
		}		
		$fd = fopen("/cache/".$cache_file_name, "wb");
		fwrite($fd, $thumbnail);
		fclose($fd);
		$cache_mtime = filemtime("/cache/".$cache_file_name);
	}
	header('Last-Modified: '.gmdate('D, d M Y H:i:s', $cache_mtime).' GMT');
	$fd = fopen("/cache/".$cache_file_name, "rb");
	$thumb_size = filesize("/cache/".$cache_file_name);
	header('Content-Length: '.$thumb_size);
	$thumbnail = fread ($fd, $thumb_size);
	fclose ($fd);
	echo $thumbnail;
}else{
	$place=$_SERVER["SCRIPT_NAME"];
	$place=substr ($place, 0, strrpos($place, "/"));
	print "<html><head><title>Idex of $place</title><meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\"><style type=\"text/css\"> a img{border: none;}</style></head><body>";
	print "<h1>Idex of $place</h1><hr>";
	print "<img src=\"/icons/back.gif\" alt=\"[DIR]\"> <a href=\"..\">Parent Directory</a><br>";	
	$FV = opendir("./") or print "Error";
	$i=0;
	while(($rfile = readdir($FV)) != false){
		if($rfile== "." or $rfile==".." or $rfile=="cache"){continue;} 
		if(is_dir($rfile)){
		print "<img src=\"/icons/folder.gif\" alt=\"[DIR]\"> <a href=\"$rfile\">$rfile</a><br>";
		}	
		$wfile[$i]=$rfile;
		$i++;	
	}
	closedir($FV);
	sort($wfile);
	foreach($wfile as $value){
		if($value== "." or $value==".." or $value=="index.php"){continue;}
		if(is_dir($value)){continue;}
		print "<a href=\"$value\"><img src=\"?f=$value\" alt=\"$value\"></a>";
	}
}
?>