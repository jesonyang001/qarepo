(function() {
    $('.badge-list').sortable({
        itemSelector: '.badge-ctnr',
        containerSelector: '.badge-list',
        onDrop: function(item, ctnr) {
            item.removeClass("dragged").removeAttr("style");
            $("body").removeClass("dragging");
            var postData = {
                badge_id: item.data('badgeId'),
                position: $('.badge-ctnr').index(item)
            }
            $.ajax({
                type: 'post',
                dataType: 'json',
                url: askbot.urls.reorderBadges,
                data: postData
            });
        }
    });
})();
