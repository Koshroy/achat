var butCnt = 0;

function initFunc()
{
    $("#add-btn").click(addTopic);
    return true;
}

function addTopic()
{
    $("#topic-lst-div").append('<button type="button" name="topicBut-'+(butCnt++)+'"class="btn btn-info"><i class="icon-remove"></i>&nbsp;&nbsp;' + $("#topic").val() + '</button>').trigger('create');
    $('button[name|="topicBut"]').click(function() { $(this).remove(); });
    $("#topic").val('');


    
}

function removeTopic(remBut)
{
    remBut.elem.removeNode(true);
}

$(document).ready(initFunc);