$( document ).ready(function() {


    $('.dropdown-button').dropdown({
        inDuration: 300,
        outDuration: 225,
        constrain_width: false, // Does not change width of dropdown to that of the activator
        hover: true, // Activate on hover
        gutter: 0, // Spacing from edge
        belowOrigin: false, // Displays dropdown below the button
        alignment: 'left' // Displays dropdown with edge aligned to the left of button
      }
    );



    var menu = $(".sections-navigator");

    // All list items
    var offset = 150;
    var menuItems = menu.find("a");

    menuItems.first().parent().addClass('selected')

    // Anchors corresponding to menu items
    var scrollItems = menuItems.map(function(){
        var item = $($(this).attr("href"));
        if (item.length) { return item; }
    });

    $('a[href*="#"]:not([href="#"]').on('click',function (e) {
	    e.preventDefault();

	    var target = this.hash;
	    var $target = $(target);

        if(!$(target+" .collapsible-header").hasClass('active')){
            $(target+" .collapsible-header").click()
        };

	    $('html, body').stop().animate({
	        'scrollTop': $target.offset().top - 80
	    }, 400, 'swing', function () {
	        window.location.hash = target;
	    });
	});

    if(window.location.hash){
        if(!$(window.location.hash+" .collapsible-header").hasClass('active')){
            $(window.location.hash+" .collapsible-header").click()
        };

        $target = $(window.location.hash)
        $('html, body').stop().animate({
            'scrollTop': $target.offset().top - 80
        }, 400, 'swing');
    }

    // Bind to scroll to update the menu
    $(window).scroll(function(){

        // Get container scroll position
        var fromTop = $(this).scrollTop() + offset;

        // Get id of current scroll item
        var cur = scrollItems.map(function(){
            if ($(this).offset().top < fromTop)
            return this;
        });

        if(cur.length == 0){
            cur = [scrollItems[0]]
        }
        // Get the id of the current element
        cur = cur[cur.length-1];
        var id = cur && cur.length ? cur[0].id : "";
        // Set/remove active class
        menuItems
        .parent().removeClass("selected")
        .end().filter("[href=#"+id+"]").parent().addClass("selected");

    });
});
