/**
 * Created by 123 on 2017/4/28.
 */
var base_url = 'http://129.132.114.28:8080/locationhunter/';
navigator.geolocation.getCurrentPosition(success, error);
var location_url = 'https://www.instagram.com/explore/locations/'
var curr_loc
var curr_rec_city
var rec_cache = {}
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
        curr_loc = city
        // Somehow transfer it to our database format in front-end
        city = 'lucerne'

        getRecommendation(city)


    })

}

function error(err) {
    console.log(err)
}
function getRecommendation(city) {
    if (city in rec_cache) {
        var result = rec_cache[city]
        var list = $(".gallery")[0]
        list.innerHTML = ''
        for (var i in result) {
            // target="_blank" href="https://www.instagram.com/explore/locations/' + result[i]['id']+'/'+ result[i]['slug']+ '"
            var item =
                '<a id="' + result[i]['id'] + '">' +
                '<figure>' +
                '<img id ="img-' + result[i]['id'] + '"src=' + result[i]['pic'] + ' alt="">' +
                '</figure>' +
                '<figcaption id="cap-' + result[i]['id'] + '">' +
                result[i]['name'] +
                '</figcaption >' +
                '<button class="accept">Accept</button>' +
                '<button class="decline">Decline</button>' +
                '</a>'

            list.innerHTML += item
        }
        curr_rec_city = result[0]['belong_city']
    }
    else {
        $.ajax({
            url: base_url + "triprec/" + city + "/",
            type: "GET",
            success: function (data, textStatus, jqXHR) {
                var result = JSON.parse(data)
                console.log(result)
                var list = $(".gallery")[0]
                list.innerHTML = ''
                for (var i in result) {
                    // target="_blank" href="https://www.instagram.com/explore/locations/' + result[i]['id']+'/'+ result[i]['slug']+ '"
                    var item =
                        '<a id="' + result[i]['id'] + '">' +
                        '<figure>' +
                        '<img id ="img-' + result[i]['id'] + '"src=' + result[i]['pic'] + ' alt="">' +
                        '</figure>' +
                        '<figcaption id="cap-' + result[i]['id'] + '">' +
                        result[i]['name'] +
                        '</figcaption >' +
                        '<button class="accept">Accept</button>' +
                        '<button class="decline">Decline</button>' +
                        '</a>'

                    list.innerHTML += item
                }
                curr_rec_city = result[0]['belong_city']
                rec_cache[curr_rec_city] = result
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Due to some reason, you can't do it now");
            }
        });
    }
}
    $(function () {
        $.ajax({
            url: base_url + "avaCities/",
            type: "GET",
            success: function (data, textStatus, jqXHR) {
                var result = JSON.parse(data)
                console.log(result)
                var availableTags = result
                $(".city-search").autocomplete({
                    source: availableTags,
                    select: function (event, ui) {
                        console.log(ui['item']['value'])
                        var city = ui['item']['value']
                        getRecommendation(city)
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

        })
        $(".container").on("click", ".accept", function () {
            // TODO:FEEDBACK TO THE SERVER
            var id = this.parentNode.id
            var pic = $("#img-" + this.parentNode.id).attr('src')
            var location_name = $("#cap-" + this.parentNode.id).text()


            $(this.parentNode).hide()
            var list = $('#selected-rec')[0]
            list.innerHTML +=
                '<div class="friend-item w3-card-4 friendelem" id="' + curr_rec_city + '">' +
                '<div class="w3-container w3-center" id="' + id + '">' +
                '<a target="_blank" href="">' +
                '<img class="imagefollower" src="' + pic + '">' +
                '</a>' +
                '<h4 id="head-'+id+'">' + location_name + '</h4>' +
                '<div class="w3-section">' +
                '<button class="btn btn-raised btn-primary friendbutton"  id="remove">Remove</button>' +
                '</div>' +
                '</div>' +
                '</div>'

        })
        $("#recommendation").on("click", "#remove", function () {

            var id = this.parentNode.parentNode.id
            var list = $(".gallery")
            var ele = list.find('#' + id)
            if (ele.length != 0) {
                ele.show()
            }
            this.parentNode.parentNode.parentNode.remove()

        })
        $("#recommendation").on("click", "#generate", function () {
            /*alert('Here We should generate a trip route plan for the user' +
                'or send a trip route email to him. the route generation is based on' +
                'the cities she is going to')*/

            var accept_ids = new Array()
            var decline_ids = new Array()
            var cities = new Array()
            var locations = new Array()

            var list_children = $("#selected-rec").children().each(function () {
                var id = $(this).children().first()[0].id
                var city = this.id
                accept_ids.push(id)
                cities.push(city)
                locations.push($("#head-"+id).text())
                //locations.push()
            });
            console.log(cities)
            $.each(rec_cache,function (key,value) {
                if($.inArray(key,cities)!=-1){
                    $.each(value,function (index,ele) {
                        if($.inArray(ele['id'],accept_ids)==-1){
                            decline_ids.push(ele['id'])
                        }
                    })
                }
            })
            console.log(rec_cache)
            console.log(locations)
            console.log(accept_ids)
            console.log(decline_ids)
            $.ajax({
                url: base_url + "genTrip/",
                type: "POST",
                data: {
                    locations: locations,
                    cities: cities,
                    curr_loc: curr_loc,
                    accept_ids:accept_ids,
                    decline_ids:decline_ids
                },
                success: function (data, textStatus, jqXHR) {
                    var status = JSON.parse(data)
                    console.log(status)
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    alert("can't generate route for you");
                }
            });
        })


    });
