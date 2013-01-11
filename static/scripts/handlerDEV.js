$(document).ready(function(){
	
	page = 1;

	
	$("#more-offers").click(function(){
		page += 1;
		$('#more-offers').before('<img style="position:relative; left:46%;" id="img-loader" src="/static/images/blue-bar-loader.gif" />');
		$.ajax({
			type: 'GET',
			url: '/page/' + page,
			dataType: 'json',
			success: function(offers){
				$('#img-loader').remove();
				if(offers[0].more == 1){
					createDivsOffers(offers);
				}
				else if(offers[0].more == 0){
					createDivsOffers(offers);
					$('#nomore-offers').remove(); //precenção de deduplicação
					$('#more-offers').after('<div id="nomore-offers" class="notification"> Todas as ofertas foram carregadas</div>');
					$('#more-offers').remove();

				}
				else{
					$('#nomore-offers').remove(); //precenção de deduplicação
					$('#more-offers').after('<div id="nomore-offers" class="notification"> Todas as ofertas foram carregadas</div>');
					$('#more-offers').remove();
				}
			}
		})
	});


	
});


function track_master(cat,act,lbl){
	_gaq.push(['_trackEvent', cat, act, lbl]);
}

function addHTMLOffers(offer){
			oferta = "<div class=\"offer\"> <a class=\"link-offer\" rel=\"nofollow\" onclick=\"track_master('offers','selected','"+offer.link+"')\" href=\""+offer.link+"\" target=\"_blank\"> <h1 class=\"title-offer\">"+offer.desc+"</h1> </a> <img class=\"img-offer\" src=\"/offers/images/"+offer.id+"\" alt=\"Imagem da Oferta\"/> <div class=\"details-offer\"><a rel=\"nofollow\" onclick=\"track_master('offers','selected','"+offer.link+"')\" href=\""+offer.link+"\" target=\"_blank\"> Mais Detalhes </a></div>	<button class=\"button\" id=\"share-button\"> Compartilhar </button> <span class=\"span_site_name\"> Fonte:<strong> "+offer.site_name+"</strong></span><div class=\"share-panel\"></div></div>";
	return oferta;
}

/*
function addShareForm(){
	return form="<div><form method=\"post\"><label for=\"frm-link\">Link</label><input name=\"frm-link\" type=\"text\" value=\"link da oferta aqui\"/><br /><hr />Enviar por Email <br /><label for=\"frm-name\">Nome</label><input type=\"text\"/><br /><label for=\"frm-from\">Seu email</label><input name=\"frm-from\" type=\"text\"/><br /><label for=\"frm-to\">Para</label><input name=\"frm-to\" type\"text\" /><br /><label for=\"message\"> Mensagem </label><textarea style=\"vertical-align:top;\" name=\"message\" rows=\"3\" cols=\"80\"></textarea><br /><button class=\"button\">Enviar</button></form></div>";
}
*/
function addShareForm(){
	return form="<div><form method=\"post\"><label for=\"frm-link\">Link</label><input name=\"frm-link\" type=\"text\" value=\"link da oferta aqui\"/>";
}

$("#offers").on("click", ".offer #share-button", function(event) {
	  div_offer = this.parentNode; //jquery is useless to do this!!!
	  if($(div_offer).children('.share-panel').children().length == 0){
	  		form = addShareForm();
		    $(form).appendTo($(div_offer).children('.share-panel'));
		    $(div_offer).css("height","484px");
	  $(div_offer).children('.share-panel').toggle('slow');//toggle triggers before set focus()
	  offer_img = div_offer.getElementsByTagName('img')[0];
	  img_href = offer_img.getAttribute('src');
	  var patt = /\/offers\/images\/(\d+)/g;
	  offer_id = patt.exec(img_href)[1];
      div_offer.getElementsByTagName('form')[0].elements['frm-link'].value = "http://www.escolhaofertas.com.br/offers/offer/"+offer_id;
	  div_offer.getElementsByTagName('form')[0].elements['frm-link'].focus();//javascript rules!

	  }else{
			$(div_offer).children('.share-panel').children().remove();
			$(div_offer).css("height","364px");
	  $(div_offer).children('.share-panel').toggle('slow');
			this.focus();

	  }
}); 


function createDivsOffers(offers){
	$.each(offers, function(index, offer){
		oferta = addHTMLOffers(offer);
		$(oferta).appendTo('#offers');
	});
}

