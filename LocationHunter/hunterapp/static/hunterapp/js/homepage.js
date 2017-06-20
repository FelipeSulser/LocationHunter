    var base_url = 'http://129.132.114.28:8080/locationhunter/';
    //var base_url = 'http://129.132.114.28:8080/locationhunter/';
    var shortMonth = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    var user_id = getCookie('user_id');
    var username = getCookie('username');
    function sortNumber(a,b) {
    return a - b;
    }
    function Comparator(a, b) {
       if (a[1] < b[1]) return -1;
       if (a[1] > b[1]) return 1;
       return 0;
    }
    function formatDate(date) {
      var monthNames = [
        "January", "February", "March",
        "April", "May", "June", "July",
        "August", "September", "October",
        "November", "December"
      ];

      var day = date.getDate();
      var monthIndex = date.getMonth();
      var year = date.getFullYear();

      return day + ' ' + monthNames[monthIndex];
}
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
    function drawLineChart(div_name,raw_data,start_date){
        var margin = {top: 50, right: 20, bottom: 50, left: 20},
            width = 500 - margin.left - margin.right,
            height = 270 - margin.top - margin.bottom;
        var parseDate = d3.time.format("%d-%b-%y").parse;
        var x = d3.time.scale().range([0, width]);
        var y = d3.scale.linear().range([height, 0]);
        var xAxis = d3.svg.axis().scale(x)
            .orient("bottom").ticks(8);
        var yAxis = d3.svg.axis().scale(y)
            .orient("left").ticks(5);
        var valueline = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.close); });
        var svg = d3.select(div_name)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
        var curr_date = start_date
        data = []
        for(index in raw_data){
            d = {}
            d['close'] = raw_data[index]['value']
            date_string = (curr_date.getDate()+"-"
                +shortMonth[curr_date.getMonth()]+"-"+(curr_date.getFullYear()-2000)).toString()
            d['date'] = date_string
            data.push(d)
            curr_date.setTime(curr_date.getTime() + (24 * 60 * 60 * 1000));
        }
        data.forEach(function(d) {
            d.date = parseDate(d.date);
            d.close = +d.close;
        });
        x.domain(d3.extent(data, function(d) { return d.date; }));
        y.domain([0, d3.max(data, function(d) { return d.close; })]);
        svg.append("path")
            .attr("class", "line")
            .attr("d", valueline(data));
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);
        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);

    }
    function drawBarChart(div_name,raw_data){
        data = [];
        for (index in raw_data){
            d = {}
            d['label'] = raw_data[index][0]
            d['value'] = raw_data[index][1]
            data.push(d)
        }
        var div = d3.select(div_name).append("div").attr("class", "toolTip");
        var axisMargin = 20,
            margin = 0,
            valueMargin = 4,
            width = parseInt(600, 10),
            height = parseInt(260, 10),
            barHeight = (height-axisMargin-margin*2)* 0.4/data.length,
            barPadding = (height-axisMargin-margin*2)*0.2/data.length,
            data, bar, svg, scale, xAxis, labelWidth = 0;
        max = d3.max(data, function(d) { return d.value; });
        svg = d3.select(div_name)
            .append("svg")
            .attr("preserveAspectRatio","xMinYMin meet")
            .classed("svg-content-responsive",true)
            .attr("width", width)
            .attr("height", height)
           
        bar = svg.selectAll("g")
            .data(data)
            .enter()
            .append("g");
        bar.attr("class", "bar")
            .attr("cx",0)
            .attr("transform", function(d, i) {
                return "translate(" + margin + "," + (i * (barHeight + barPadding) + barPadding) + ")";
            });
        bar.append("text")
            .attr("class", "label")
            .attr("y", barHeight / 2)
            .attr("fill",function(d,i){return "#286090"})
            .attr("dy", ".35em") //vertical align middle
            .text(function(d){
                return d.label;
            }).each(function() {
                labelWidth = Math.ceil(Math.max(labelWidth, this.getBBox().width));
        });
        scale = d3.scale.linear()
            .domain([0, max])
            .range([0, width - margin*2 - labelWidth]);
          
           
        bar.append("rect")
            .attr("transform", "translate("+labelWidth+", 0)")
            .attr("height", barHeight)
            .attr("fill",function(d,i){return "#286090"})
            .attr("width", function(d){
                return scale(d.value);
            });
        bar.append("text")
            .attr("class", "value")
            .attr("y", barHeight / 2)
            .attr("dx", -valueMargin + labelWidth) //margin right
            .attr("dy", ".35em") //vertical align middle
            .attr("text-anchor", "end")
            .text(function(d){
                return (d.value);
            })
            .attr("x", function(d){
                var width = this.getBBox().width;
                return Math.max(width + valueMargin, scale(d.value));
            });
        /*
        bar.on("mousemove", function(d){
                div.style("left", d3.event.pageX+10+"px");
                div.style("top", d3.event.pageY-25+"px");
                div.style("display", "inline-block");
                div.html((d.label)+"<br>"+(d.value)+"%");
            });
        bar.on("mouseout", function(d){
                div.style("display", "none");
            });*/
        svg.insert("g",":first-child")
            .attr("class", "axisHorizontal")
            .attr("transform", "translate(" + (margin + labelWidth) + ","+ (height - axisMargin - margin)+")")
    }



    $(document).ready(function(){

        $( ".friend-list" ).on( "click", "#accept", function() {
                var clicked_user = this.parentNode.parentNode;
                var clicked_name =  clicked_user.getElementsByTagName("h4")[0].innerHTML
                $.ajax({
                    url : base_url+"fof/action/",
                    type: "POST",
                    data : {
                                csrfmiddlewaretoken: "{{ csrf_token }}",
                                related_name:clicked_name,
                                related_id:clicked_user.id,
                                action:'accept'
                            },
                    success: function(data, textStatus, jqXHR)
                    {
                        result = JSON.parse(data)
                        if(result['type']=='OK') {
                            $(clicked_user).hide();
                        }else{
                            $.toast({
                                text: result['type'], // Text that is to be shown in the toast
                                heading: 'Message:', // Optional heading to be shown on the toast
                                showHideTransition: 'slide', // fade, slide or plain
                                allowToastClose: true, // Boolean value true or false
                                hideAfter: 3000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                                stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                                position: 'bottom-left', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                                
                                
                                
                                textAlign: 'left',  // Text alignment i.e. left, right or center
                                loader: false,  // Whether to show loader or not. True by default
                                beforeShow: function () {}, // will be triggered before the toast is shown
                                afterShown: function () {}, // will be triggered after the toat has been shown
                                beforeHide: function () {}, // will be triggered before the toast gets hidden
                                afterHidden: function () {}  // will be triggered after the toast has been hidden
                    });
                             //alert(result['type'])
                        }

                    },
                    error: function (jqXHR, textStatus, errorThrown)
                    {
                        alert("Due to some reason, you can't do it now")

                    }
                });
                    $.ajax({
                    url : base_url+"logAction/"+getCookie('user_id')+"/fof/accept/",
                    type: "POST",
                    data : {
                                csrfmiddlewaretoken: "{{ csrf_token }}",
                                related_name:clicked_name,
                                related_id:clicked_user.id,
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
        });
        $( ".friend-list" ).on( "click", "#decline", function() {
               var clicked_user = this.parentNode.parentNode;
               var clicked_name =  clicked_user.getElementsByTagName("h4")[0].innerHTML;
               $.ajax({
                    url : base_url+"fof/action/",
                    type: "POST",
                    data : {
                                csrfmiddlewaretoken: "{{ csrf_token }}",
                                related_name:clicked_name,
                                related_id:clicked_user.id,
                                action:'decline'
                            },
                    success: function(data, textStatus, jqXHR)
                    {
                        result = JSON.parse(data)
                        if(result['type']=='OK') {
                            $(clicked_user).parent().hide();
                        }else{
                            alert(result['type'])
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown)
                    {
                        alert("Due to some reason, you can't do it now");
                    }
               });
               $.ajax({
                    url : base_url+"logAction/"+getCookie('user_id')+"/fof/decline/",
                    type: "POST",
                    data : {
                                csrfmiddlewaretoken: "{{ csrf_token }}",
                                related_name:clicked_name,
                                related_id:clicked_user.id,
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
        });
        $( ".locations-list" ).on( "click", "#declineLoc", function() {
               var clicked_user = this.parentNode.parentNode;
               var clicked_name =  clicked_user.getElementsByTagName("h4")[0].innerHTML;
               $.ajax({
                    url : base_url+"recLocations/action/",
                    type: "POST",
                    data : {
                                csrfmiddlewaretoken: "{{ csrf_token }}",
                                related_name:clicked_name,
                                related_id:clicked_user.id,
                                action:'decline'
                            },
                    success: function(data, textStatus, jqXHR)
                    {
                        result = JSON.parse(data)
                        if(result['type']=='OK') {
                            $(clicked_user).parent().hide();
                        }else{
                            alert(result['type'])
                        }
                    },
                    error: function (jqXHR, textStatus, errorThrown)
                    {
                        alert("Due to some reason, you can't do it now");
                    }
               });
        });
        $(".refresh").click(function () {

            var list = $(".friend-list")[0];
            while (list.firstChild) {
                list.removeChild(list.firstChild);
            }
            console.log(list);
             $.toast({
                        text: "Fetching Friends Recommendations", // Text that is to be shown in the toast
                        heading: 'Message:', // Optional heading to be shown on the toast
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 3000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: false, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'bottom-left', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        
                        
                        
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: false,  // Whether to show loader or not. True by default
                        beforeShow: function () {}, // will be triggered before the toast is shown
                        afterShown: function () {}, // will be triggered after the toat has been shown
                        beforeHide: function () {}, // will be triggered before the toast gets hidden
                        afterHidden: function () {}  // will be triggered after the toast has been hidden
                    });
            $.ajax({
                //url: base_url + "fof/",
                url: base_url + "similarFof/",
                type: "POST",
                data: {
                    csrfmiddlewaretoken: "{{ csrf_token }}",
                    user: user_id
                },
                success: function (data, textStatus, jqXHR) {
                    var friends = JSON.parse(data)

                    var list = $(".friend-list")[0]

                    $.toast({
                        text: "Friends Refreshed!", // Text that is to be shown in the toast
                        heading: 'Message:', // Optional heading to be shown on the toast
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 3000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: false, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'bottom-left', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        
                        
                        
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: false,  // Whether to show loader or not. True by default
                        beforeShow: function () {}, // will be triggered before the toast is shown
                        afterShown: function () {}, // will be triggered after the toat has been shown
                        beforeHide: function () {}, // will be triggered before the toast gets hidden
                        afterHidden: function () {}  // will be triggered after the toast has been hidden
                    });

                    var instgram_url = 'https://www.instagram.com/'
                    for (i in friends){
                        var friend_item =
                            "<div class='friend-item w3-card-4 friendelem' >" +
                                "<div class='w3-container w3-center' id='"+friends[i]['user_id']+"'>"+
                                    "<a href='"+instgram_url+friends[i]['username']+"/'>"+
                                        "<img class='imagefollower' src='"+friends[i]['img_url']+"'/>"+
                                    "</a>"+
                                    "<h4>"+friends[i]['username']+"</h4>"+
                                    "<div class='w3-section'>"+
                                        "<button class='btn btn-raised btn-primary friendbutton' id='accept' >Accept</button>"+
                                        "<button class='btn btn-raised btn-secondary friendbutton' id='decline' >Dismiss</button>"+
                                    "</div>"+
                                "</div>"
                            "</div>"
                            list.innerHTML+= friend_item
                    }
                },
            });
        });
        $(".refreshLoc").click(function () {

            var list = $(".locations-list")[0];
            while (list.firstChild) {
                list.removeChild(list.firstChild);
            }
            console.log(list);
            $.ajax({
                //url: base_url + "fof/",
                url: base_url + "similarLocation/",
                type: "POST",
                data: {
                    csrfmiddlewaretoken: "{{ csrf_token }}",
                    user: user_id
                },
                success: function (data, textStatus, jqXHR) {
                    var locs = JSON.parse(data)
     
                    var list = $(".locations-list")[0]
                    var instgram_url = 'https://www.instagram.com/' 
                    for (i in locs){
                        var friend_item =
                            "<div class='loc-item locElem' >" +
                                "<div class='' id='"+locs[i]['loc_id']+"'>"+
                                    "<a target='_blank' href='"+instgram_url+locs[i]['username']+"/'>"+
                                        "<img class='imagefollower' src='"+locs[i]['img_url']+"'/>"+
                                    "</a>"+
                                    "<h4>"+locs[i]['name']+"</h4>"+
                                    "<div class='w3-section'>"+
                                        "<button class='btn btn-raised btn-secondary locbutton' id='declineLoc' >Dismiss</button>"+
                                    "</div>"+
                                "</div>"
                            "</div>"
                            list.innerHTML+= friend_item
                    }
                },
            });
        });


        user_id = getCookie('user_id');
        username = getCookie('username');
        $.get(base_url+"user/details", function(data, status){
            user_detail = JSON.parse(data);
            if(user_detail.error){
                window.location.replace(base_url);
            }else {

                datafollowers = user_detail['followers_trend'];
                console.log(user_detail);
                var myL = [];
                myL.push(formatDate(new Date(datafollowers[0].date *1000)))
          for(var x = 0; x < user_detail['followers_trend'].length -2; x++){
            myL.push('');
          }
          myL.push(formatDate(new Date(datafollowers[datafollowers.length-1].date *1000)));
          seriesval = [];
          var meanval = Math.floor(datafollowers.length/2);
          myL[meanval] = formatDate(new Date(datafollowers[meanval].date*1000));
          for(var x = 0; x < datafollowers.length; x++){
            seriesval.push(datafollowers[x].value);
          }

          followedval = []
          for(var x = 0; x < user_detail['followed_people_trend'].length; x++){
            followedval.push(user_detail['followed_people_trend'][x].value);
          }

          //plot with followers and followed by
        new Chartist.Line('#chartActivity', {
          labels: myL,
          series: [
           seriesval,
           followedval
          ]
        }, {lineSmooth: Chartist.Interpolation.simple({
    divisor: 2
  }),
            seriesBarDistance: 10,
            axisX: {
                showGrid: false
            },
            height: "245px"
        }, ['screen and (max-width: 640px)', {
            seriesBarDistance: 5,
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]);
        //Chartist.Line('#chartActivity', data, options, responsiveOptions);
                $("#media_count").html(user_detail['media_count']);
                $("#follower_count").html(user_detail['num_followers']);
                $("#follow_count").html(user_detail['num_followed_people']);
                console.log("USER DETAIL");
                console.log(user_detail);

                if(user_detail['email_digest'] === 'on'){
                    $("#emaildigest").html("ACTIVE");
                }else{
                    $("#emaildigest").html("OFF");
                }
                //drawLineChart('.follower_trend',user_detail['followers_trend'],new Date(user_detail['start_time']))
                //drawLineChart('.media_trend',user_detail['media_trend'],new Date(user_detail['start_time']))
                //drawLineChart('.follow_trend',user_detail['followed_people_trend'],new Date(user_detail['start_time']))
                //console.log(user_detail['hashtags'])
                //drawBarChart('.hashtag_trend',user_detail['hashtags'])
 

                var total=  0;
                var myNumbers = [];
                var myLabels = [];
                for(var x = 0; x < user_detail['hashtags'].length; x++){
                    myNumbers.push(user_detail['hashtags'][x][1]);
                    myLabels.push(user_detail['hashtags'][x][0]);
                }
                

                var data = {
                    labels : myLabels,
                    series:myNumbers
                };
                var options = {
                  labelInterpolationFnc: function(value) {
                    return value[0]
                  },
                  donut:true,
                  donutWidth:40
                };
                var responsiveOptions = [
                  ['screen and (min-width: 640px)', {
                    chartPadding: 20,
                    labelOffset: 50,
                    labelDirection: 'explode',
                    labelInterpolationFnc: function(value) {
                      return value;
                    }
                  }],
                  ['screen and (min-width: 1024px)', {
                    labelOffset: 50,
                    chartPadding: 35
                  }]
                ];

                new Chartist.Pie('#chartPreferences', data,options,responsiveOptions);

                //console.log(user_detail['like_historic'])
                var mylist = [];
                for(var i = 0; i < user_detail['like_historic'].length; i++){
                    var myobj = {};
                    myobj['date'] = new Date(user_detail['like_historic'][i][1]*1000);
                    myobj['count'] =  user_detail['like_historic'][i][0];
                    mylist.push(myobj);
                }
                var chartData = mylist;
               
               
                var chart1 = calendarHeatmap()
                              .data(chartData)
                              .selector('#chart-one')
                              .colorRange(['#dee6ed','#337AB7'])
                              //green traditional github color palette
                              //.colorRange(['#D8E6E7', '#218380'])
                              .tooltipEnabled(true)
                              .onClick(function (data) {
                                console.log('onClick callback. Data:', data);
                              });
                chart1();  // render the chart
            }
        });
        $.ajax({
            //url : base_url+"fof/",
            url: base_url + "similarFof/",
            type: "POST",
            data : {
                        csrfmiddlewaretoken: "{{ csrf_token }}",
                        user:user_id
                    },
            success: function(data, textStatus, jqXHR)
            {
                console.log("Getting Similar FOF");
                console.log(data);
                var friends = JSON.parse(data)

                var list = $(".friend-list")[0]
                var instgram_url = 'https://www.instagram.com/' 
                for (i in friends){
                    var friend_item =
                        "<div class='friend-item friendelem' >" +
                            "<div class='' id='"+friends[i]['user_id']+"'>"+
                                "<a target='_blank' href='"+instgram_url+friends[i]['username']+"/'>"+
                                    "<img class='imagefollower' src='"+friends[i]['img_url']+"'/>"+
                                "</a>"+
                                "<h4>"+friends[i]['username']+"</h4>"+
                                "<div class='w3-section'>"+
                                    "<button class='btn btn-raised btn-primary friendbutton' id='accept' >Follow</button>"+
                                    "<button class='btn btn-raised btn-secondary friendbutton' id='decline' >Dismiss</button>"+
                                "</div>"+
                            "</div>"
                        "</div>"
                        list.innerHTML+= friend_item
                }
            },
            error: function (jqXHR, textStatus, errorThrown)
            {

            }
        });
    $.ajax({
            //url : base_url+"fof/",
            url: base_url + "similarLocation/",
            type: "POST",
            data : {
                        csrfmiddlewaretoken: "{{ csrf_token }}",
                        user:user_id
                    },
            success: function(data, textStatus, jqXHR)
            {
                console.log("Getting Similar Location");
                console.log(data);
                var locs = JSON.parse(data)
 
                var list = $(".locations-list")[0]
                var instgram_url = 'https://www.instagram.com/' 
                for (i in locs){
                    var friend_item =
                        "<div class='loc-item locElem' >" +
                            "<div class='' id='"+locs[i]['loc_id']+"'>"+
                                "<a target='_blank' href='"+instgram_url+locs[i]['username']+"/'>"+
                                    "<img class='imagefollower' src='"+locs[i]['img_url']+"'/>"+
                                "</a>"+
                                "<h4>"+locs[i]['name']+"</h4>"+
                                "<div class='w3-section'>"+
                                    "<button class='btn btn-raised btn-secondary locbutton' id='declineLoc' >Dismiss</button>"+
                                "</div>"+
                            "</div>"
                        "</div>"
                        list.innerHTML+= friend_item
                }
            },
            error: function (jqXHR, textStatus, errorThrown)
            {

            }
        });


    });