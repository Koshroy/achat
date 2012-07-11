var butCnt = 0;

var currPos;
var posValid = false;


function initFunc()
{
    $("#add-btn").click(addTopic);
    $("#general-form").submit(sendForm);
    $("#use-curr-loc").click(function() {$("#spec-loc-div").toggle(!this.checked);});

    if (navigator.geolocation)
    {
	navigator.geolocation.getCurrentPosition(
	    function(pos) { currPos = pos; posValid=true;},
	    function () { $("#use-curr-loc").hide(); });
    }

    else { $("#use-curr-loc").hide(); }

    return true;
}

function addTopic()
{
    // var old_html = $("#topic-lst-div").html();
    // $("#topic-lst-div").html(old_html + '<button type="button" name="topicBut-'+(butCnt++)+'"class="btn btn-info"><i class="icon-remove"></i>&nbsp;&nbsp;' + $("#topic").val());
    $("#topic-lst-div").append('<button type="button" name="topicBut-'+butCnt+'"class="btn btn-info"><i class="icon-remove"></i>&nbsp;&nbsp;<span name="topicButCont-' + butCnt++ + '">' + $("#topic").val() + '</span></button>');
    $('button[name|="topicBut"]').click(function() { $(this).remove(); });
    $("#topic").val('');
    return false;

}

function getURL(location, params)
{
    document.location = location + '?' + $.param(params);
}

function removeTopic(remBut)
{
    remBut.elem.removeNode(true);
}

function sendForm()
{
    var lat, lng;
    var validLatLng = false;

    if (!posValid)
    {
	var geocoder = new google.maps.Geocoder();
	geocoder.geocode({'address':$("#spec-loc").val()}, 
			  function(results, status) 
			  {
			      if (status == google.maps.GeocoderStatus.OK)  
			      {
				  lat = results.latLng.lat();
				  lng = results.latLng.lng();
				  validLatLng = true;
			      }
			  });
    }
    else 
    {
	lat = currPos.coords.latitude;
	lng = currPos.coords.longitude;
	validLatLng = true;
    }
    var latStr='', lngStr='';
    if (validLatLng) {latStr = '' + lat; lngStr = '' + lng;}
    var tops = new Array();
    $('span[name|="topicButCont"]').each(
	function() { tops.push($(this).html()); }
    );
    // postForm('/formtest', 
    // 	      {
    // 		  topics: tops.join(),
    // 		  name: $("#disp-name").val(),
    // 		  gender_self: $("#gender-self").val(),
    // 		  gender_target: $("#gender-target").val(),
    // 		  lat: latStr,
    // 		  lng: lngStr
    // 	      });

    $("#chat-topics").val(tops.join());
    $("#chat-name").val($("#disp-name").val());
    $("#chat-gender-self").val($("#gender-self").val());
    $("#chat-gender-target").val($("#gender-target").val());
    $("#chat-lat").val(latStr);
    $("#chat-lng").val(lngStr);

    $("#chat-req-form").submit();

    return false;
    
}

$(document).ready(initFunc);

