/*!
 * Start Bootstrap - Freelancer Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('body').on('click', '.page-scroll a', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});

// Floating label headings for the contact form
$(function() {
    $("body").on("input propertychange", ".floating-label-form-group", function(e) {
        $(this).toggleClass("floating-label-form-group-with-value", !! $(e.target).val());
    }).on("focus", ".floating-label-form-group", function() {
        $(this).addClass("floating-label-form-group-with-focus");
    }).on("blur", ".floating-label-form-group", function() {
        $(this).removeClass("floating-label-form-group-with-focus");
    });
});

// Highlight the top nav as scrolling occurs
$('body').scrollspy({
    target: '.navbar-fixed-top'
})

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});

$( document ).ready(function() {
	placeNotice();
});

$( window ).resize(function() {
  placeNotice();
});
$(".navbar-fixed-top").resize(function() {
  placeNotice();
});

function placeNotice(){
	var newTop = ($(".navbar-fixed-top").css("height")).split('px')[0];
	//var width = ($("notice").css("width")).split('px')[0];
	
	if(newTop<100){
		newTop-=($(".navbar-fixed-top").css("padding-bottom")).split('px')[0];
	}
	newTop += 'px';
	console.log(newTop);
    $(".notice").css("top",newTop);
	
	
}