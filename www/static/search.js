
$(document).ready(function(){
	$('#loading').hide()

	$('#search').submit(function(e) {
		e.preventDefault();
		args = $(this).serialize();	
		$('#graph').empty();
		$('#results').empty();		

		$('#loading').show()
		$.get('/search?'+ args, function(data) {
			$('#loading').hide()
			console.log(data);
			// $('#graph').empty();
			// $('#results').empty();
			$.each(data.result, function(i, item) {
				search_result_archive(item);
			});
			graph(data);		
		});
	});

});

function search_result_archive(a) {	
	$('<div/>', {
		id: a.archive,
		class: "archive",
	}).appendTo('#results');
	$('#' + a.archive).append("<h3>" + a.archive + "</h3>");
	$.each(a.results, function(i, r) {
		$('<ul/>', {
			id: r.thread + "-" + a.archive,
			text: r.thread.replace('_', ' ')
		}).appendTo('#' + a.archive);
		let hits = "<ul>";

		console.log("---")
		
		$.each(r.hits, function(j, h){

			console.log(h)

			let hit = '<li><a href="' + h.url+ '">' + h.subject + '</a> -- <i>' + h.author_name + '</i></li>';
			hits += hit;
		});
		hits += "</ul>";
		$('#' + r.thread + "-" + a.archive).append(hits);

		console.log("***");

	});
}

var min_month = new Date(1995, 9);
var max_month = new Date();

function diff_months(d1, d2) {
    var months;
    months = (d2.getFullYear() - d1.getFullYear()) * 12;
    months -= d1.getMonth();
    months += d2.getMonth();
    return months <= 0 ? 0 : months;
}

function format(date) {
  var month_names = [
    "Jan", "Feb", "Mar",
    "Apr", "May", "Jun", "Jul",
    "Aug", "Sep", "Oct",
    "Nov", "Dec"
  ];
  return month_names[date.getMonth()] + ' ' + date.getFullYear();
  //return date.getMonth() + ' - ' + date.getFullYear();
}


function graph(data) {
	var d = diff_months(min_month, max_month);
	var vec = new Array();
	for(let ar of data.result) {
		let ar_vec = new Array(d + 1).fill(0);
		ar_vec[0] = ar.archive;
		for(let r of ar.results) {
			let date = new Date(Date.parse(r.thread.replace("_", " 1, "))); // this may blow...
			let index = diff_months(min_month, date);
			ar_vec[index  + 1] = r.nbr_hits;
		}
		vec.push(ar_vec);
	}
	

	// var x_axis = new Array(d + 1);
	// x_axis[0] = 'x';
	// for (let i = 1; i < d+1; i++) {
	// 	let d = new Date(min_month.getFullYear(), min_month.getMonth());
	// 	d.setMonth(d.getMonth() + (i - 1));
	// 	x_axis[i] = format(d);
	// }

	// vec.push(x_axis);

	var x_axis = new Array(d);
	for (let i = 0; i < d; i++) {
		let d = new Date(min_month.getFullYear(), min_month.getMonth());
		d.setMonth(d.getMonth() + i);
		x_axis[i] = format(d);
	}


	console.log(vec);

	var chart = c3.generate({
	    bindto: '#graph',	    
	    data: {
	      	columns: vec,
	      	type: 'bar'
	    },
	    axis: {
	    	x: {
	    		type: 'category',
	    		categories: x_axis,
	    		tick: {
	    			culling: {
	    				max: 15
	    			},
	    			multiline:false
	    		}
	    	}
	    },
	    bar: {
	        width: {
	            ratio: 0.8
	        }
    	}
	});
}





























