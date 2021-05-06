$(document).ready(function () {
    $('.btn-tweet-filter').on('click', function () {
      var $target = $(this).data('target');
      console.log('Target->' + $target)
      if ($target != 'Covid Info') {
        $('.table-tweet tr').css('display', 'none');
        $('.table-tweet tr[data-status="' + $target + '"]').fadeIn('slow');
      } else {
        $('.table-tweet tr').css('display', 'none').fadeIn('slow');
      }
    });

    $('.btn-hashtag-filter').on('click', function () {
      var $target = $(this).data('target');
      console.log('Target->' + $target)
      if ($target != 'All') {
        $('.table-htag tr').css('display', 'none');
        $('.table-htag tr[data-status="' + $target + '"]').fadeIn('slow');
      } else {
        $('.table-htag tr').css('display', 'none').fadeIn('slow');
      }
    });
 });