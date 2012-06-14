var callInterval = 200;
var connected = false;
var disconnected = false;

function initFunc()
{
    $("#chatform").submit(chatpress);
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
				   addToChat("Person 2", data.text);
			       }
			   }
		       }
		       , 'json');
	    }

	},
	callInterval
    );
    
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

function addToChat(id, s)
{
    var h = $("#chatarea").html();
    $("#chatarea").html(h + "<tr><td>"+id+"</td><td>"+s+"</td></tr>");
}

function dispStatus(s)
{
    $("#conn_status").html("<p>"+s+"</p>");
}

function clearBox()
{
    addToChat("Person 1", $("#chatbox").val());
    $("#chatbox").val("");
}

function chatpress()
{
    if ($("#chatbox").val() == "") return false;
    $.post("/sendmsg", 
	   {
	       message: $("#chatbox").val(),
	       uniq_id: $("#uniq_id").val()
	   }, clearBox, 'text')
    return false;

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

$(document).ready(initFunc);