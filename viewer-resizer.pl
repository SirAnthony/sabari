#!/usr/bin/perl
# Это перловая версия.

my $VER = "1.2";

use Time::HiRes qw(gettimeofday);
my $start = gettimeofday;
use MIME::Types;
use Digest::MD5 qw(md5_hex);
#use CGI::Carp qw(fatalsToBrowser);
my $types = MIME::Types->new;
my $part = "/var/www/site";
my $cache = "/var/www/cache/";

use strict;
#use warnings;


if($ENV{'REQUEST_METHOD'} eq 'GET'){
	urldecode(\$ENV{'QUERY_STRING'});
	my ($name, $value) = split(/=/, $ENV{'QUERY_STRING'});
	putdata(\$name, \$value);
}else{
	die "Content-type: text/html; charset=utf8\n\n Фиг";
}

sub urldecode{
	my($val)=@_;
	${$val}=~s/\+/ /g;
	${$val}=~s/%([0-9A-H]{2})/pack('C',hex($1))/ge;
}

sub imageworks{
	my($md) = shift;
	my($val) = shift;
	if(-e ${$md}){
		use Image::Size qw/imgsize/;
		my ($w, $h) = imgsize("$part${$val}");
		warn $! if $!;
		return 'ext', $w, $h;
	}else{
		use Image::Magick;
		my $picsize = 200; ## Size of image will create
		my $image = Image::Magick->new();
		my $path = $part.${$val};
		open(IMAGE, $path)
			or ( warn $!, " $path" && return 'fail');
		$image->Read(\*IMAGE);
		#$image->Read("$path");
		close(IMAGE);
		my($ox,$oy) = $image->Get("width", "height");
		my($w, $h) = $ox,$oy;
		if($ox < $oy){
			if($oy > $picsize){$oy = int(($ox/$oy)*$picsize); $ox = $picsize;
			}
		}else{
			if($ox > $picsize){$ox = int(($oy/$ox)*$picsize); $oy = $picsize;}
		}
		my $er = $image->Thumbnail(width=>$oy, height=>$ox);
		warn $er if $er;
		$er = $image->Write(${$md});
		warn $er, " $path" if $er;
		return 'fail' if $er;
		
		print "Thumbinail creation. Page need to reload<br/>";
		return 'crt', $w, $h;
	}
}

sub putdata{
	my($name, $value) = @_;	
	if(${$name} eq "d"){
		my $vn = 'valign="top" align="center"';
		print "Content-type: text/html; charset=utf8\n\n";
		print <<ENDH;
<html>
	<head>
		<title>Index of ${$value}</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<link href="/styles/mainst.css" rel="stylesheet" type="text/css">
		<style>a img{border: 0px;}</style>
	</head>
	<body>
		<h1>Idex of ${$value}</h1>
		<hr><table><tr>
		<td class="t1" $vn>
			<a href=".."><img src="/icon/back.png" width="165" height="165" alt="Parent"><br>Parent Directory</a>
		</td>
ENDH
		opendir(DR, "$part"."${$value}") or print "$!";
		my @cont = readdir(DR);
		closedir(DR);
		my $fl = 0;
		my $td = 2;
		my $cols = 5;
		while($fl != 2){
			foreach my $elm (@cont){
				next if $elm =~ /^\./;
				if(!$fl){
					if( -d $part.${$value}.$elm ){
						$td = 1 if $td > $cols;
						print "<td class=\"t$td\" $vn><a href=\"${$value}$elm/\"><img src=\"/icon/folder.png\" width=\"165\" height=\"165\" alt=\"Dir\"><br>$elm</a></td>";
						print "</tr><tr>" if $td == $cols;
						$td++;
					}
				}else{
					if( -f $part.${$value}.$elm ){
						my $tp = $types->mimeTypeOf("$elm");
						$td = 1 if $td > $cols;
						#print $tp,"<br>";
						if($tp =~ /^image\/(?!vnd.djvu)/){
							my $hval = md5_hex(${$value}.$elm);
							my $md = \ ($cache.$hval);
							my ($result, $width, $height) = imageworks($md, \ (${$value}.$elm));
							if ($result eq "ext"){
								print '<td class="t'.$td.'" '.$vn.'><a href="'.${$value}.$elm.'" target="_blank"><img src="/cache/'.$hval.'" alt="img" title="'.$width.'x'.$height.'"></a></td>';
							}elsif($result eq 'fail'){
								print '<td class="t'.$td.'" '.$vn.'><a href="'.${$value}.$elm.'">Thumbinal creation failed.</a></td>';
							}else{
								print '<td class="t'.$td.'" '.$vn.'><a href="'.${$value}.$elm.'">Thumbinal created.</a></td>';
							}
						}else{
							$tp =~ s/\//-/g;
							print "<td class=\"t$td\" $vn><a href=\"${$value}$elm\"><img src=\"/icon/$tp.png\" width=\"165\" height=\"165\"><br>$elm</a></td>";
						}
						print "</tr><tr>" if $td == $cols;
						$td++;
					}
				}
			}
			$fl++;
			my $end = gettimeofday;
			my $res = $end-$start;
			print "</tr></table><hr><p class=\"ft\"><a href=\"http://code.google.com/p/sabari/\">Sabari</a> v".$VER."<br>Время выполнения скрипта: ", $res, " c.<br>Original script by <a href=\"mailto:anthony\@adsorbtion.org\">Sir Anthony</a></p>" if $fl == 2;
		}
	}elsif(${$name} eq "f"){
	#for safety cache or stand alone thumbinal.
	#usage <img src="link.to.script?f=filename"> 
		use Digest::MD5 qw(md5_hex);
		my $md = \ ($cache.md5_hex(${$value}));
		my $result = imageworks($md, $value);
		if( $result eq "ext" || $result eq "crt"){
			print "Content-Type: ", $types->mimeTypeOf("${$value}"),";\nContent-Length: ", -s ${$md} , ";\n\n";
			use IO::File;
			open(FLE, "<".${$md});
			while(<FLE>){
				print $_;
			}
			close(FLE);
			my @file = <FLE>;
			my $file = IO::File->new($cache.md5_hex(${$value}), "<");
			$file->autoflush();
			print $file->getlines;
			$file->close;

		}else{
			print "Content-Type: text/html;\n\n";
			print "Ошибка создания миниатюры: $!";
		}
	}else{
		print "Content-type: text/html; charset=utf8\n\n Параметр-корявко";
	}
}

