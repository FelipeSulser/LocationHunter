/**
 * Created by 123 on 2017/4/19.
 */
var graph_data_map = {};
var currenthashtag = null;
var d1  = null;
var selected_hashtags = []
$(document).ready(function () {
    $("#overlay-content").on("click", ".expand", function () {
        console.log(undo);
        console.log("EXPAND CLICKED")
        $('#graph-overlay').show();
      
       
        $("#alldata").prepend(undo);
        var hashtag = this.parentNode.parentNode.id;
        currenthashtag = hashtag;
        $.get("/locationhunter/locationtags/" + hashtag, function (data, status) {
             console.log("RECIEVED DATA");
             $('#graph-overlay').hide()
            if (data != '404 Not found') {

                var graph_data = JSON.parse(data);
                console.log(graph_data)
                graph_data_map[hashtag] = graph_data
                //$("#mygraph").height(500);
                var entities = graph_data
                var keys = Object.keys(entities)
                var nodes = []
                var edges = []
                var count = 0 
                for (var i = 0; i < keys.length; i += 1) {
                    if (keys[i] == '#stats' || keys[i] == hashtag) {
                        continue
                    } else {
                        var node = {}
                        node['name'] = keys[i]
                        nodes.push(node)
                        var edge = {}
                        edge['source'] = count;
                        edge['target'] = keys.length - 2
                        edge['weight'] = count += 1
                        edges.push(edge)
                    }
                }
                var center_node = {}
                center_node['name'] = hashtag
                center_node['radius'] = 20
                nodes.push(center_node)
                drawDAG(hashtag, nodes, edges)
            } else {
                alert('Cannot Expand graph due to some reasons')
            }
        });
        var my_ht = $(event.target).text();
        RELATED_HASHTAGS_URL = "/locationhunter/relatedHashtags/";
        $.ajax({
            type: "POST",
            url: RELATED_HASHTAGS_URL,
            data: {
                csrfmiddlewaretoken: "{{ csrf_token }}",   // < here
                state: "inactive",
                hashtag: my_ht
            },
            success: function (data) {
               
            }
        }); 
         document.getElementById("scrollhere").scrollIntoView();
      

    });
   
    $("body").on("click", "#copy", function () { 
        var hashtags = "";
        $.each($("#selected-hashtags").children(),function(key,value){
            if(key%2==0){
                hashtags+="#"+value.innerHTML;
            }
        });
        var copyFrom = $('<textarea/>');
        copyFrom.css({
             position: "absolute",
             left: "-1000px",
             top: "-1000px",
        });
        copyFrom.text(hashtags);
        $('body').append(copyFrom);
        copyFrom.select();
        document.execCommand('copy');
    });

    $("body").on("click", "#send", function () { 
        console.log('send message')
        var hashtags = "";
        $.each($("#selected-hashtags").children(),function(key,value){
            if(key%2==0){
                hashtags+="#"+value.innerHTML;
            }
        });
        $.ajax({
            type: "POST",
            url: '/locationhunter/sendMessage/',
            data: {
                message:hashtags
            },
            success: function (data) {
                alert(JSON.parse(data)['type'])
            }
        }); 
    });

    $("body").on('click',".hashtag",function(){  
            var index = selected_hashtags.indexOf(this.id);
            if (index >= 0) {
                selected_hashtags.splice( index, 1 );
                if (selected_hashtags.length==0) {
                    $("#copy").hide()
                    $("#send").hide()
                };
            }
            $(this).prev().remove();
            this.remove();
           
    });
});
function drawDAG(hashtag, nodes, edges) {
    
    if(d1 == null){
        d1 = new Graphic("#hashtag-graph");
        var func = {}
        func['name'] = function(n){
            return "Add Hashtags"
        };
        func['action'] = function(n){
            var tag = n.data.name
            if(selected_hashtags.indexOf(tag)==-1){
                var tag_list = $('#selected-hashtags')[0]
                tag_list.innerHTML += "<li >"+tag+"</li><input type='button' class = 'hashtag btn btn-primary btn-raised' value='remove' id='"+tag+"'>";
                selected_hashtags.push(tag);
                if (selected_hashtags.length==1){
                     $("#copy").show()
                     $("#send").show()
                };
            }
        };
        d1.add_menu_function('_add',func)
    }
    var graph = {}
    graph['nodes'] = nodes
    graph['links'] = edges
    d1.removeAll();
    d1.update();
    d1.merge_graphic(graph);
    d1.update();
}
function copyToClipboard(text) {
    if (window.clipboardData) { // Internet Explorer
        window.clipboardData.setData("Text", text);
    } else {  
        unsafeWindow.netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");  
        const clipboardHelper = Components.classes["@mozilla.org/widget/clipboardhelper;1"].getService(Components.interfaces.nsIClipboardHelper);  
        clipboardHelper.copyString(text);
    }
}