$( document ).ready(function() {
 $('.ui.accordion')
        .accordion()


  var menu = $(".navigator");

  // All list items
  var offset = 150;
  var menuItems = menu.find("a");

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
});