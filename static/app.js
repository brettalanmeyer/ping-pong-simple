$(function(){

	var left = $("#left");
	var right = $("#right");

	// var socket = io.connect("http://" + document.domain + ":" + location.port + "/pingpong");
	var socket = io.connect();

	console.log("http://" + document.domain + ":" + location.port + "/pingpong");

	socket.on("response", function(data) {
		left.html(data.left);
		right.html(data.right);
    });

});