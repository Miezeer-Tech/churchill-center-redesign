document.querySelectorAll('details.more').forEach(function(d){d.addEventListener('toggle',function(){var p=d.parentElement;if(p)p.classList.toggle('open-clamp',d.open)})});
