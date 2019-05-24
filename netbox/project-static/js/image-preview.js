$('a[rel=image-preview-popover]').popover({
  html: true,
  trigger: 'hover',
  placement: 'right',
  content: function(){return '<img src="'+$(this).attr('href') + '" />';}
});
