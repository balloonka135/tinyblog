$(document).ready(function(){

	var url = $(location).attr('href');
	var tit = $(this).attr('title');

	var tshare = "http://www.twitter.com/share?url="+url
	var fshare = "https://www.facebook.com/sharer/sharer.php?u="+url
	var gshare = "https://plus.google.com/share?url="+url
	var lshare = "https://www.linkedin.com/shareArticle?mini=true&url="+url+"&title="+tit+"&summary=&source="

	console.log(lshare);
	$('.socialshare .twitter a').attr('href', tshare );
	$('.socialshare .face a').attr('href', fshare );
	$('.socialshare .gplus a').attr('href', gshare );
	$('.socialshare .linkedin a').attr('href', lshare );


});
