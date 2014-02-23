$(document).ready(function(){

	var url = $(location).attr('href');
	var tit = $(this).attr('title');
	var text_share = "Veja este site sobre #python"

	var tshare = "http://www.twitter.com/share?url="+url+"&via=berlottocdd&text="+text_share
	var fshare = "https://www.facebook.com/sharer/sharer.php?u="+url+"&t="+tit
	var gshare = "https://plus.google.com/share?url="+url
	var lshare = "https://www.linkedin.com/shareArticle?mini=true&url="+url+"&title="+tit+"&summary=&source="

	$('.socialshare .twitter a').attr('href', tshare );
	$('.socialshare .face a').attr('href', fshare );
	$('.socialshare .gplus a').attr('href', gshare );
	$('.socialshare .linkedin a').attr('href', lshare );

});
