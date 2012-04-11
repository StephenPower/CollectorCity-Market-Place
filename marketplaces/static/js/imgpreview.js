/*
 * imgPreview jQuery plugin
 * Copyright (c) 2009 James Padolsey
 * j@qd9.co.uk | http://james.padolsey.com
 * Dual licensed under MIT and GPL.
 * Updated: 09/02/09
 * @author James Padolsey
 * @version 0.21
 */
(function(c){c.expr[':'].linkingToImage=function(b,f,a){return!!(c(b).attr(a[3])&&c(b).attr(a[3]).match(/\.(gif|jpe?g|png|bmp)$/i))};c.fn.imgPreview=function(f){var a=c.extend({imgCSS:{},distanceFromCursor:{top:10,left:10},preloadImages:true,onShow:function(){},onHide:function(){},onLoad:function(){},containerID:'imgPreviewContainer',containerLoadingClass:'loading',thumbPrefix:'',srcAttr:'href'},f),d=c('<div/>').attr('id',a.containerID).append('<img/>').hide().css('position','absolute').appendTo('body'),e=c('img',d).css(a.imgCSS),g=this.filter(':linkingToImage('+a.srcAttr+')');function h(b){return b.replace(/(\/?)([^\/]+)$/,'$1'+a.thumbPrefix+'$2')}if(a.preloadImages){g.each(function(){(new Image()).src=h(c(this).attr(a.srcAttr))})}g.mousemove(function(b){d.css({top:b.pageY+a.distanceFromCursor.top+'px',left:b.pageX+a.distanceFromCursor.left+'px'})}).hover(function(){var b=this;d.addClass(a.containerLoadingClass).show();e.load(function(){d.removeClass(a.containerLoadingClass);a.onLoad.call(e[0],b)}).attr('src',h(c(b).attr(a.srcAttr)));a.onShow.call(d[0],b)},function(){d.hide();e.unbind('load').attr('src','');a.onHide.call(d[0],this)});return this}})(jQuery);


