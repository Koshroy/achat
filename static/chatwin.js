var callInterval = 200;
var connected = false;
var disconnected = false;

var testing = true;

function initFunc()
{
    $("#chatform").submit(chatpress);
    if (!testing)
    {
	setInterval(
	    function()
	    {
		if (!connected && !disconnected)
		{
		    tryConnect();
		}
		else if (!disconnected) {

		    $.post("/recvmsg", 
			   {
			       uniq_id: $("#uniq_id").val()
			   },
			   function(data) {
			       if (data.msg == 'event')
			       {
				   if (data.text == 'stopped') 
				   {
				       connected = false;
				       disconnected = true;
				       dispStatus("Disconnected.");
				   }
			       }
			       else {
				   if (data.text != '') {
				       addToChat("Stranger", data.text);
				   }
			       }
			   }
			   , 'json');
		}

	    },
	    callInterval
	);
    }

    $("#chatdiv").css("height", (screen.height - 280)+"px");
    $("#chatdiv").css("overflow", "auto");

    
    return true;
}

function tryConnect()
{
    $.post("/chatconnect",
	   {
	       uniq_id: $("#uniq_id").val(),
	       req: 'start'
	   },
	   function (data) {
	       if (data == 'connected')
	       {
		   dispStatus("Connected!");
		   connected = true;
	       }
	       else if (data == 'waiting')
	       {
		   dispStatus("Waiting for a connection.");
	       }
	       else if (data == 'stopped')
	       {
		   connected = false;
		   disconnected = true;
		   dispStatus("Disconnected.");
	       }
	   },
	   'text'
	  );
}

function showOverlay()
{
    $("#change-overlay").css("display", "inline");
    $("#over-box").css("display", "inline");
}

function hideOverlay()
{
    $("#change-overlay").css("display", "none");
    $("#over-box").css("display", "none");
}

function addToChat(id, s)
{
    $("#chatarea").append("<tr><td>"+id+"</td><td>"+s+"</td></tr>");
}

function dispStatus(s)
{
    $("#conn_status").html("<p>"+s+"</p>");
}

function clearBox()
{
    addToChat("You", $("#chatbox").val());
    $("#chatbox").val("");
}

function chatpress()
{
    if (!testing)
    {
	if ($("#chatbox").val() == "") return false;
	if (!connected || disconnected) return false;
	$.post("/sendmsg", 
	       {
		   message: $("#chatbox").val(),
		   uniq_id: $("#uniq_id").val()
	       }, clearBox, 'text')
	return false;
    }
    else
    {
	clearBox();
    }

}

function disconnect()
{
    if (connected)
    {
	$.post("/chatconnect",
	       {
		   uniq_id: $("#uniq_id").val(),
		   req: 'stop'
	       },
	       function (data) {
		   connected = false;
		   if (data == 'success')
		   {
		       dispStatus("Disconnected.");
		   }
		   else
		   {
		       dispStatus("Error.");
		   }
	       },
	       'text'
	      );

	return false;
    }
}

function nextChatWin()
{
    showOverlay();
}

function gotoNextChat()
{
    disconnect();
    location.reload();
    return false;
    
}

$(document).ready(initFunc);