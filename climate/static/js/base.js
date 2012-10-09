function initFileUploads() {
	$('input[type=file]').each(function(){
		var fake = $('<div class="fakefile"><button></button><input type="text" class="fake" disabled="disabled"/></div>');
		fake.find('button').html($(this).attr('title'));
		$(this).addClass('file hidden').after(fake);
		$(this).change(function(){
			$(this).next().find('input').val($(this).val().split('\\').pop());
		});
	});
}

(function ($) {	
	/**
	* base on 
	* @author Remy Sharp
	* @url http://remysharp.com/2007/01/25/jquery-tutorial-text-box-hints/
	*/
	$.fn.hint = function (blurClass) {
	  if (!blurClass) { 
	    blurClass = 'blur';
	  }
	    
	  return this.each(function () {	    
	    // capture the rest of the variable to allow for reuse
	    var title = $(this).attr('title');

	    // only apply logic if the element has the attribute
	    if (title) { 
	      // on blur, set value to title attr if text is blank
	      $(this).blur(function () {
	        if ($(this).val() === '') {
	        	$(this).val(title).addClass(blurClass);
	        }
	      }).focus(function(){
	    	if ($(this).val() === title && $(this).hasClass(blurClass)) {
	    		$(this).val('').removeClass(blurClass);
  	        }
	      }).blur(); // now change all inputs to title
	    }
	  });
	};
})(jQuery);

$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});