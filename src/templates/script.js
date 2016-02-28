$( document ).ready(function() {
    //
    // Side menu
    //
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


    // Hash
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


    // Hash
    if(window.location.hash){
        if(!$(window.location.hash+" .collapsible-header").hasClass('active')){
            $(window.location.hash+" .collapsible-header").click()
        };

        $target = $(window.location.hash)
        $('html, body').stop().animate({
            'scrollTop': $target.offset().top - 80
        }, 400, 'swing');
    }

    var options = {
        keys: ['name'],
        threshold: 0.15
    }
    var searchClasses, searchFunctions, searchVariables ;

    $.getJSON('search.json', function(json){
        searchClasses = new Fuse(json['classes'], options);
        searchFunctions = new Fuse(json['functions'], options);
        searchVariables = new Fuse(json['variables'], options);

        console.log("Done");
    })

    var search = function(term){
        var max = 30;

        console.log(term);
        searchResult = searchClasses.search(term)
        for(var i=0;i<searchResult.length;i++){ searchResult[i].type = 'class' }

        if(searchResult.length < max){
            var funcs = searchFunctions.search(term);
            for(var i=0;i<funcs.length;i++){ funcs[i].type = 'function' }
            searchResult.push.apply(searchResult, funcs)
        }

        if(searchResult.length < max){
            var vars = searchVariables.search(term);
            for(var i=0;i<vars.length;i++){ vars[i].type = 'variable' }
            searchResult.push.apply(searchResult, vars)
        }

        var searchElm = $('#search-result');
        searchElm.html("");


        if (searchResult.length == 0) {
            searchElm.hide()
        } else {
            searchElm.show()
        }

        var num = max;
        if(searchResult.length < max) num = searchResult.length;

        for(var i=0;i<num;i++){
            var res = searchResult[i];
            var el = $('<li>');
            var link = $('<a href="' + res.url + '">');

            el.append(link);

            if(res['class']){
            link.append('<span class="searchClass">'+res['class']+'.</span>')
            }
            link.append('<span class="searchName">'+res.name+'</span>')

            link.append('<span class="searchType">' + res.type + '</span>');
            searchElm.append(el)
        };
    }

    $('#search').bind('input', function() {
        search($(this).val())
    });
});
