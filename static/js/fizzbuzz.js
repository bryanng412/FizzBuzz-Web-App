$(function() {
	$("#dialButton").click(function() {
		$.ajax({
			url: "/getNumber",
			data: $("form").serialize(),
			type: "POST",
			success: function(response) {
				location.reload();
				console.log(response);
			},
			error: function(error) {
				alert("Error: Invalid Entry");
				console.log(error);
			}
		});
	});
});


$(function() {
	$(".redialButton").click(function() {
		var date = $(this).attr("date")
		$.ajax({
			url: "/redial/"+date,
			data: $("form").serialize(),
			type: "GET",
			success: function(response) {
				location.reload();
				console.log(response);
			},
			error: function(error) {
				alert("Error");
				console.log(error);
			}
		});
	});
});