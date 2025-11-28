
/* global $ */

$(document).ready(function () {
  //////////////////////// Prevent closing from click inside dropdown
// some scripts

// jquery ready start
$(document).ready(function () {
  //////////////////////// Prevent closing from click inside dropdown
  $(document).on('click', '.dropdown-menu', function (e) {
    e.stopPropagation();
  });

  $('.js-check :radio').change(function () {
    var check_attr_name = $(this).attr('name');
    if ($(this).is(':checked')) {
      $('input[name=' + check_attr_name + ']')
        .closest('.js-check')
        .removeClass('active');
      $(this).closest('.js-check').addClass('active');
    } else {
      item.removeClass('active');
      // item.find('.radio').find('span').text('Unselect')
    }
  });

  $('.js-check :checkbox').change(function () {
    var check_attr_name = $(this).attr('name');
    if ($(this).is(':checked')) {
      $(this).closest('.js-check').addClass('active');
      // item.find('.radio').find('span').text('Add')
    } else {
      $(this).closest('.js-check').removeClass('active');
      // item.find('.radio').find('span').text('Unselect')
    }
  });
  ////////////////////// Bootstap tooltip
  if ($('[data-toggle="tooltip"]').length > 0) {
    $('[data-toggle="tooltip"]').tooltip();
  } // end if

  // jquery end

  // ✅ Auto-hide Django/Bootstrap alerts after 4 seconds
  setTimeout(function () {
    $('#message').fadeOut('slow');
  }, 4000);
});
