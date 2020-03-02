$(document).ready(function() {
    $('#table-temperatur').DataTable( {
		"lengthMenu": [[10, 50, 100, 500, 1000, -1], [10, 50, 100, 500, 1000, "All"]],
		"paging": true,
		"pagingType": "full_numbers",
		"order": [[ 1, "desc"]]
	});
} );



