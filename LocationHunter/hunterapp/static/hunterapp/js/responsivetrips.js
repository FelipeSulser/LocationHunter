/**
 * Created by 123 on 2017/4/28.
 */
var base_url = 'http://129.132.114.28:8080/locationhunter/';
navigator.geolocation.getCurrentPosition(success, error);
var location_url = 'https://www.instagram.com/explore/locations/'
var globalResult = []
    function getCookie(cname) {
            var name = cname + "=";
            var decodedCookie = decodeURIComponent(document.cookie);
            var ca = decodedCookie.split(';');
            for(var i = 0; i <ca.length; i++) {
                var c = ca[i];
                while (c.charAt(0) == ' ') {
                    c = c.substring(1);
                }
                if (c.indexOf(name) == 0) {
                    return c.substring(name.length, c.length);
                }
            }
            return "";
    }
function success(position) {

    var GEOCODING = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + position.coords.latitude + '%2C' + position.coords.longitude + '&language=en';

    $.getJSON(GEOCODING).done(function (location) {
        /*$('#country').html(location.results[0].address_components[5].long_name);
         $('#state').html(location.results[0].address_components[4].long_name);
         $('#city').html(location.results[0].address_components[2].long_name);
         $('#address').html(location.results[0].formatted_address);
         $('#latitude').html(position.coords.latitude);
         $('#longitude').html(position.coords.longitude);*/
        var city = location.results[0].address_components[4].long_name
        console.log(city)
        // Somehow transfer it to our database format in front-end
        city = 'lucerne'
        getRecommendation(city)


    })

}

function error(err) {
    console.log(err)
}
function getRecommendation(city) {

    $.ajax({
        url: base_url + "triprec/" + city + "/",
        type: "GET",
        success: function (data, textStatus, jqXHR) {
            var result = JSON.parse(data)
            globalResult = result
            console.log(result)
            var list = $(".gallery")[0]
            console.log("LIST IS:");
            console.log(list);
            list.innerHTML = ''
            $("#selected-rec").innerHTML = '' 
            for (var i in result) {
                // target="_blank" href="https://www.instagram.com/explore/locations/' + result[i]['id']+'/'+ result[i]['slug']+ '"
                var item =
                    '<a id="' + result[i]['id'] + '" lat="'+result[i]['lat']+'"  lon="'+result[i]['lon']+'" label="'+result[i]['name'] +'"  class="galleryitem">' +
                    '<figure>' +
                    '<img id ="img-' + result[i]['id'] + '"src=' + result[i]['pic'] + ' alt="">' +
                    '</figure>' +
                    '<figcaption id="cap-' + result[i]['id'] + '">' +
                    result[i]['name'] +
                    '</figcaption >' +
                    '<button class="accept btn btn-raised btn-primary">Visit</button>' +
                    '<button class="decline btn btn-raised btn-secondary">Discard</button>' +
                    '</a>'

                list.innerHTML += item
            }
             $("#loading-overlay").hide(); 
            //console.log("Loading overlay now invisible");
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $("#loading-overlay").hide(); 
            alert("Due to some reason, you can't do it now");
        }
    });


}
$(function () {
    $.ajax({
        url: base_url + "avaCities/",
        type: "GET",
        success: function (data, textStatus, jqXHR) {
            var result = JSON.parse(data)
            console.log(result)
            var availableTags = result
            console.log("Avacities ajax executed");
            $(".city-search").autocomplete({
                source: availableTags,
                select: function (event, ui) {
                     $("#loading-overlay").show();
                     //console.log($("#loading-overlay"));
                     //console.log("Showing loading");
                    console.log(ui['item']['value'])
                    var city = ui['item']['value']
                    getRecommendation(city);   
                }
            });
        },
        error: function (jqXHR, textStatus, errorThrown) {
            alert("City List Unreachable");
        }
    });
    $(".container").on("click", ".decline", function () {
        // TODO:FEEDBACK TO THE SERVER

        $(this.parentNode).hide()
        $.ajax({
            url : base_url+"logAction/"+getCookie('user_id')+"/location/decline/",
            type: "POST",
            data : {
                        csrfmiddlewaretoken: "{{ csrf_token }}",
                        action:'decline'
                    },
            success: function(data, textStatus, jqXHR)
            {
                console.log("Logging successfull")
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                console.log("Logging failed")   
            }
       });

    })

    $(".container").on("click", ".accept", function () {
        // TODO:FEEDBACK TO THE SERVER
        console.log("Inside accept click event");
        //Remove the statically generated  map image if found
        $("#static_map").remove()
        $.ajax({
            url : base_url+"logAction/"+getCookie('user_id')+"/location/accept/",
            type: "POST",
            data : {
                        csrfmiddlewaretoken: "{{ csrf_token }}",
                        action:'decline'
                    },
            success: function(data, textStatus, jqXHR)
            {
                console.log("Logging successfull")
            },
            error: function (jqXHR, textStatus, errorThrown)
            {
                console.log("Logging failed")   
            }
       });

        var id = this.parentNode.id
        var lat = this.parentNode.getAttribute('lat')
        var lon = this.parentNode.getAttribute('lon')
        var label = this.parentNode.getAttribute('label')
        
        console.log(lat + " " + lon)
        var pic = $("#img-" + this.parentNode.id).attr('src')
        var location_name = $("#cap-" + this.parentNode.id).text()
        $(this.parentNode).hide()
        var list = $('#selected-rec')[0]
        list.innerHTML +=
            
            '<a  class="galleryitem friendelem" id="'+id+'"    >' +
            '<img class="imagefollower" id="'+id+'"   src="' + pic + '"   lat="'+lat+'" lon="'+lon+'"  label="'+label+'" >' +
            '</figure>' +
            '<figcaption>'+
             location_name +
            '</figcaption>'+
            '<button class="btn btn-raised btn-primary" id="removebtn">Remove</button>'+
            '</a>'; 
    })
    $("#recommendation").on("click", "#removebtn", function () {
        console.log("Inside remove click event");
        var id = this.parentNode.id;
        var list = $(".gallery")
        var ele = list.find('#' + id)
        if (ele.length != 0) {
            //ele.show();
            $(ele).show();
        }
        this.parentNode.remove()

    })
    $("#generate").click(function () {
        var locations = new Array();
        var list_children = $("#selected-rec").children().each(function(){
            //locations.push($(this).children().first()[0].id)
            console.log($(this).children().first()[0]);
            //locations.push($(this).children().first()[0].id);
            //locations.push($(this).children().first()[0].getAttribute('lat'));
            //locations.push($(this).children().first()[0].getAttribute('lon'));
            locations.push({
            	id: $(this).children().first()[0].id, 
            	lat: $(this).children().first()[0].getAttribute('lat'),
            	lon: $(this).children().first()[0].getAttribute('lon'), 
            	label: $(this).children().first()[0].getAttribute('label')
            });

        });
        console.log(locations)


        //Construct the Google Images URL 
        var GOOGLE_IMG = "https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyAK6CGZEgTUPdT9PEy533vhVPQ0eqLRSRg"
       
        //markers = "&markers=color:blue%7Clabel:S%7C40.702147,-74.015794&markers=color:green%7Clabel:G%7C40.711614,-74.012318&markers=color:red%7Clabel:C%7C40.718217,-73.998284"
        markers = ""
       	center_lat = 0.0
       	center_lon = 0.0
        locations.forEach(function(loc){
        	markers += "&markers="
        	markers += "color:blue%7Clabel:"+  loc['label'][0]  +"%7C"    //Print only the first letter)
        	markers = markers + loc['lat']  + "," + loc['lon']

        	center_lat += parseFloat(loc['lat'])
        	center_lon += parseFloat(loc['lon'])
        })
       
        center_lat = center_lat / locations.length
        center_lon = center_lon / locations.length


        //center = "&center=Brooklyn+Bridge,New+York,NY"
        center = "&center=" + center_lat.toString() + "," + center_lon.toString()

        zoom = "&zoom=15"
        size = "&size=850x350"
        maptype = "&maptype=roadmap"

        GOOGLE_IMG = GOOGLE_IMG + center + zoom + size + maptype + markers

        console.log("Generated urL")
        console.log(GOOGLE_IMG)

        $("#selected-rec").html("<img id='static_map'  src = '"+GOOGLE_IMG+"'    width='80%' />")

    })


});