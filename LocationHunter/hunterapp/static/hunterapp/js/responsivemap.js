var rtype = "";

    //Used to Fetch Popular Posts/Hashtags given a city name and a country Name
    //city Name is the city's full name, country name


function fetchPosts(city_name, country_name) {
    //Show Loading Screen
    $("#loading-overlay").show();
    POPULAR_POSTS_URL = "/locationhunter/popularPost/";
    //Redirect User to that page:
    //window.location = POPULAR_POSTS_URL + "?country=" + country_name + "&city=" + city_name;
    var myToast2 = $.toast({
        heading: 'Information',
        text: 'Please wait while we fetch the best hashtags for you!',
        icon: 'info',
        hideAfter: false
    });
    console.log(POPULAR_POSTS_URL);
    console.log("Posting : " + city_name + " " + country_name);
    $.ajax({
        type: "POST",
        url: POPULAR_POSTS_URL,
        data: {
            csrfmiddlewaretoken: "{{ csrf_token }}",   // < here
            state: "inactive",
            city: city_name, country: country_name
        },
        success: function (data) {
            console.log(data);
            myToast2.update({
                heading: 'Influencers',
                text: 'Thank you for waiting, here are your candidates',
                icon: 'success',
                hideAfter: false,
                loader: false
            });
            //Dump Contents into the Overlay
            //Destroy Old Accordion if Found
            if ($("#overlay-content").hasClass("ui-accordion")) {
                $('#overlay-content').accordion('destroy');
            }

            //Clear Old Items
            $("#overlay-content").html("");

            //Check If Valid Response
            if (data.trim() == "error") {
                $.toast({
                    heading: 'Error',
                    text: 'Could not find location',
                    showHideTransition: 'fade',
                    icon: 'error',
                    loader: false
                });
                $("#overlay-content").append("<li class='sidebar-card'>Sorry.. Not Found :(</li>");
            } else {
                //var hashtags = data.trim().split(" ");
                //hashtags.forEach(function(tag){
                //  $("#overlay-content-list").append("<li class='sidebar-card'>"+tag+"</li>");
                //});

                //Parse JSON Object
                var response_object = JSON.parse(data);
                response_object.forEach(function (tagObject) {
                    $("#overlay-content").append("<h3>" + tagObject['tag:'] + "</h3>");
                    var detail_content =
                        "<div  id = '" + tagObject['tag:'] + "'>" +
                        "<div class='detail-content'>" +
                        "<button class='btn btn-primary' type='button' style='margin:10px'>" +
                        "Score <span class='badge' id='score'>" + tagObject['score'] + "</span>" +
                        "</button>" +
                        "<button class='btn btn-primary' type='button' style='margin:10px'>" +
                        "Count <span class='badge' id='count'>" + tagObject['count'] + "</span>" +
                        "</button>" +
                        "<button style='margin:10px;display:block' class='expand btn btn-primary'>Navigate</button>" +
                        "</div>" +
                        "</div>";
                    $("#overlay-content").append(detail_content)
                });


                //Activate Accordion
                $("#overlay-content").accordion({
                    collapsible: true,
                    active: false
                });

            }
            $("#sidebar-overlay").css({"visibility": "visible"});
            //Hide Loading Screen
            $("#loading-overlay").hide();
        }
    }).fail(function (jqxhr, textStatus, error) {
        var err = textStatus + ", " + error;
        console.log("Request Failed: " + err);
        //Hide Loading Screen
        $("#loading-overlay").hide();
        alert("An Error Has Occurred ");
    });
}


function fetchInfluencers(city_name, country_name) {
    //Show Loading Screen
    $("#loading-overlay").show();
    POPULAR_INFLUENCERS_URL = "/locationhunter/popularInfluencers/";
    var myToast = $.toast({
        heading: 'Information',
        text: 'Please wait while we fetch your partners! We are making sure that we find the perfect match for you!',
        icon: 'info',
        hideAfter: false
    });

    $.ajax({
        type: "POST",
        url: POPULAR_INFLUENCERS_URL,
        data: {
            csrfmiddlewaretoken: "{{ csrf_token }}",   // < here
            state: "inactive",
            city: city_name, country: country_name
        },
        success: function (data) {
            myToast.update({
                heading: 'Influencers',
                text: 'Thank you for waiting, here are your candidates',
                icon: 'success',
                hideAfter: false,
                loader: false
            });
            console.log("Fetched the Influencers . . . ");
            console.log(data);
            var response_object = JSON.parse(data);
            //Dump Contents into the Overlay
            //$("#overlay-content").html(data);
            var maxval = 0;
            for (var i = 0; i < response_object.length; i++) {
                if (response_object[i]['score'] > maxval) {
                    maxval = response_object[i]['score'];
                }
            }
            console.log(maxval);

            //Clear Old Items
            if ($("#overlay-content").hasClass("ui-accordion")) {
                $('#overlay-content').accordion('destroy');
            }
            $("#overlay-content").html("");
            if (data.trim() == "error") {
                $.toast({
                    heading: 'Error',
                    text: 'Could not find location',
                    showHideTransition: 'fade',
                    icon: 'error'
                });
                $("#overlay-content").append("<li class='sidebar-card'>Sorry.. Not Found :(</li>");
            } else {

                response_object.forEach(function (userObj) {
                    console.log(userObj);
                    $("#overlay-content").append("<h3>" + userObj['user_data']['username'] + "</h3>");
                    var profile_pic_url = userObj['user_data']['profile_pic_url'];
                    var user_profile_link = userObj['user_data']['url_link'];
                    var user_id = userObj['user_data']['userid'];
                    //$("#overlay-content").append(mystr);
                    var myscore = ((100 * userObj['score']) / maxval).toFixed(1);

                    //Add Contents to Accordion
                    //Use image as a link
                    var generated_content =
                        "<div class='influencer-div' id="+userObj['user_data']['username']+">" +
                        "<a href='" + user_profile_link + "' target='_blank'><img class='influencer-pic' src='" + profile_pic_url + "' /></a>" +
                        "<p class='influencer-p' >Similarity : " + myscore + "\%</p>" +
                        "<div class='w3-section' id='"+user_id+"'>" +
                        "<button class='btn btn-raised btn-primary friendbutton' id='accept' >Accept</button>" +
                        "<button class='btn btn-raised btn-secondary friendbutton' id='decline' >Decline</button>" +
                        "</div>" +
                        "</div>"
                    $("#overlay-content").append(generated_content);
                });
                $("#overlay-content").accordion({
                    collapsible: true,
                    active: false,
                    heightStyle: 'content'
                });
            }
            $("#sidebar-overlay").css({"visibility": "visible"});
            //Hide Loading Screen
            $("#loading-overlay").hide();
        }
    }).fail(function (jqxhr, textStatus, error) {
        var err = textStatus + ", " + error;
        console.log("Request Failed: " + err);
        //Hide Loading Screen
        $("#loading-overlay").hide();
        alert("An Error Has Occurred ");
    });

}


function initMap() {

    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 47.372086, lng: 8.541176},
        zoom: 10
    });
    var card = document.getElementById('pac-card');
    var input = document.getElementById('pac-input');
    var types = document.getElementById('type-selector');
    var strictBounds = document.getElementById('strict-bounds-selector');

    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(card);

    var autocomplete = new google.maps.places.Autocomplete(input);

    // Bind the map's bounds (viewport) property to the autocomplete object,
    // so that the autocomplete requests use the current map bounds for the
    // bounds option in the request.
    autocomplete.bindTo('bounds', map);

    var infowindow = new google.maps.InfoWindow();
    var infowindowContent = document.getElementById('infowindow-content');
    infowindow.setContent(infowindowContent);
    var marker = new google.maps.Marker({
        map: map,
        anchorPoint: new google.maps.Point(0, -29)
    });

    autocomplete.addListener('place_changed', function () {
        infowindow.close();
        marker.setVisible(false);
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.

            $.toast({
                heading: 'Error',
                text: 'Invalid Place',
                showHideTransition: 'fade',
                icon: 'error',
                loader: false
            });
            return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);  // Why 17? Because it looks good.
        }
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);

        var address = '';
        if (place.address_components) {
            address = [
                (place.address_components[0] && place.address_components[0].short_name || ''),
                (place.address_components[1] && place.address_components[1].short_name || ''),
                (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');


            //Always the first component
            city_name = place.address_components[0].short_name;
            last_index = place.address_components.length - 1;
            country_name = place.address_components[last_index].short_name;
            console.log("City Name: " + city_name);
            console.log("Country Name: " + country_name);
            console.log(place);

            //Fetch Data
            var reqType = $("#requestType").val();
            console.log("Requesting : " + reqType);
            rtype = reqType;
            if (reqType == "hashtags") {
                fetchPosts(city_name, country_name);
            } else if (reqType == "influencers") {
                fetchInfluencers(city_name, country_name);
            } else {
                alert("Unrecognized Request Type");
            }

        }

        //Display on Marker on Map
        infowindowContent.children['place-icon'].src = place.icon;
        infowindowContent.children['place-name'].textContent = place.name;
        //infowindowContent.children['view_posts_button'].textContent = "View Popular Posts";
        infowindow.open(map, marker);
    });

    //Autocomplete with City Name Only
    autocomplete.setTypes(['(cities)']);

}