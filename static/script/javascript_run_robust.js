// // Old code (uncomment if the other one does not work perfectly):
//   window.addEventListener( "pageshow", function ( event ) {
//   var historyTraversal = event.persisted || 
//                          ( typeof window.performance != "undefined" && 
//                               window.performance.navigation.type === 2 );
//   if ( historyTraversal ) {
//     // Handle page restore.
//     window.location.reload();
//   }
// });

// // New code (this works well):
var perfEntries = performance.getEntriesByType("navigation");
if (perfEntries[0].type === "back_forward") {
    location.reload(true);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $("input[name$='network_selection']").click(function() {
        var test = $(this).val();
        $("div.desc_").hide();
        // $("#provided-network-selection").hide();
        if (test=='Yes'){
          $("#provided-network-selection").show();
          $("#div_upload_custom_ppi_network").hide();
        }
        else{
          $("#provided-network-selection").hide();
          $("#div_upload_custom_ppi_network").show();
        }
    });
});











function download_values_case_study(){
  var dropdown = document.getElementById("download_case_study_data");
  var selection = dropdown.value;
  // console.log(selection);
  // var emailTextBox = document.getElementById("textbox_seeds");
  // emailTextBox.value = selection;

  //var btn = document.querySelector('#select');

  if (selection=='COVID-19') {
            // $("#hidden_div_normalizeBy_custom2").trigger('click')
          document.getElementById("hidden_div_normalizeBy_custom2")[0].click();
          // document.getElementById("hidden_div_normalizeBy_custom2").click();
            // $("#hidden_div_normalizeBy_custom2").selected();
          // document.getElementById("alpha").value=0.25;
          // document.getElementById("alpha_slider").value=0.25;
          // document.getElementById("beta").value=0.9;
          // document.getElementById("beta_slider").value=0.9;
          // document.getElementById("n").value=30;
          // document.getElementById("tau").value=0.1;
          // document.getElementById("tau_slider").value=0.1;
          // document.getElementById("gamma").value=1.00;
          // document.getElementById("gamma_slider").value=1.00;
          // document.getElementById("textbox_seeds").value = 'TLR4 NLRP3 MBL2 IL6 IL1RN IL1B CX3CR1 CCR5 AGT ACE F2';
          // document.getElementById("selectOne_NodeNamespace").value = 0
          // document.getElementById("selectOne_Normalize").value=1
          // document.getElementById("inbuilt_network_selection").value=0
} else {
          document.getElementById("alpha").value=0.25;
          document.getElementById("alpha_slider").value=0.25;
          document.getElementById("beta").value=0.9;
          document.getElementById("beta_slider").value=0.9;
          document.getElementById("n").value=30;
          document.getElementById("tau").value=0.1;
          document.getElementById("tau_slider").value=0.1;
          document.getElementById("gamma").value=1.00;
          document.getElementById("gamma_slider").value=1.00;
          document.getElementById("textbox_seeds").value = 'P63092 P35354 P01229 P01148 Q5JWF2 P84996 O95467 P05019';
          document.getElementById("selectOne_NodeNamespace").value = 3
          document.getElementById("selectOne_Normalize").value=1
          document.getElementById("inbuilt_network_selection").value=0
}
          

}









document.getElementById('download_case_study_data').addEventListener('click', function(){
if(this.checked)
  document.getElementById('hidden_div_normalizeBy_custom2').click();
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function reset_values_case_study(){
    var dropdown = document.getElementById("use_case_study_data");
    var selection = dropdown.value;
    console.log(selection);
    var emailTextBox = document.getElementById("textbox_seeds");
    emailTextBox.value = selection;

    if (selection=='COVID-19') {
            document.getElementById("alpha").value=0.25;
            document.getElementById("alpha_slider").value=0.25;
            document.getElementById("beta").value=0.9;
            document.getElementById("beta_slider").value=0.9;
            document.getElementById("n").value=30;
            document.getElementById("tau").value=0.1;
            document.getElementById("tau_slider").value=0.1;
            document.getElementById("gamma").value=1.00;
            document.getElementById("gamma_slider").value=1.00;
            document.getElementById("textbox_seeds").value = 'TLR4 NLRP3 MBL2 IL6 IL1RN IL1B CX3CR1 CCR5 AGT ACE F2';
            document.getElementById("selectOne_NodeNamespace").value = 0
            document.getElementById("selectOne_Normalize").value=1
            document.getElementById("inbuilt_network_selection").value=0
} else if (selection=='Precocious puberty') {
            document.getElementById("alpha").value=0.25;
            document.getElementById("alpha_slider").value=0.25;
            document.getElementById("beta").value=0.9;
            document.getElementById("beta_slider").value=0.9;
            document.getElementById("n").value=30;
            document.getElementById("tau").value=0.1;
            document.getElementById("tau_slider").value=0.1;
            document.getElementById("gamma").value=1.00;
            document.getElementById("gamma_slider").value=1.00;
            document.getElementById("textbox_seeds").value = 'P63092 P35354 P01229 P01148 Q5JWF2 P84996 O95467 P05019';
            document.getElementById("selectOne_NodeNamespace").value = 3
            document.getElementById("selectOne_Normalize").value=1
            document.getElementById("inbuilt_network_selection").value=0
}
            

  }

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/* Hide 'Custom PPI network upload' hidden div on loading of page: */
$("#div_upload_custom_ppi_network").hide();
$(document).ready(function(){
    $('input[type="radio"]').click(function(){
        var inputValue = $(this).attr("value");
        var targetBox = $("." + inputValue);
        $(".box").not(targetBox).hide();
        $(targetBox).show();
    });
});
    
/* Upload or fill in seeds: */
document.getElementById('inputfile_seeds')
.addEventListener('change', function() {
var fr=new FileReader();
fr.onload=function(){
    document.getElementById('textbox_seeds')
            .textContent=fr.result;
}  
fr.readAsText(this.files[0]);
})



/* Show either inbuilt PPI network options or hidden div containing 'Upload Custom network' button and textbox, based on radio button click: */


/* Uploading custom PPI network: */
document.getElementById('uploaded_ppi_network_filename')
                      .addEventListener('change', function() {
                        
                      var fr=new FileReader();
                      fr.onload=function(){
                          document.getElementById('network_contents')
                                  .textContent=fr.result;
                      }
                        
                      fr.readAsText(this.files[0]);
                  })

/* Show div containing 'Upload custom study bias data' button and textbox on selection of value 'Custom' from 'Normalize by' dropdown menu: */
function showDiv(divId, element)
{
    document.getElementById(divId).style.display = element.value == 3 ? 'block' : 'none';
}

function showDiv2(divId1, divId2, element)
{
    document.getElementById(divId1).style.display = element.value == 'COVID-19' ? 'block' : 'none';
    document.getElementById(divId2).style.display = element.value == 'Precocious puberty' ? 'block' : 'none';
}

/* Upload custom study bias data: */
document.getElementById('inputfile_studybiasdata')
                        .addEventListener('change', function() { 
                        var fr=new FileReader();
                        fr.onload=function(){
                            document.getElementById('custom_studybiasdata_contents_textbox')
                                    .textContent=fr.result;
                        } 
                        fr.readAsText(this.files[0]);
                    })



function resetValues(){
            document.getElementById("alpha").value=0.25;
            document.getElementById("alpha_slider").value=0.25;
            document.getElementById("beta").value=0.9;
            document.getElementById("beta_slider").value=0.9;
            document.getElementById("n").value=30;
            document.getElementById("tau").value=0.1;
            document.getElementById("tau_slider").value=0.1;
            document.getElementById("gamma").value=1.00;
            document.getElementById("gamma_slider").value=1.00;
            document.getElementById("textbox_seeds").value = 'TLR4 NLRP3 MBL2 IL6 IL1RN IL1B CX3CR1 CCR5 AGT ACE F2'; // COVID-19 case study
}

function resetValues_pp(){
            document.getElementById("alpha").value=0.25;
            document.getElementById("alpha_slider").value=0.25;
            document.getElementById("beta").value=0.9;
            document.getElementById("beta_slider").value=0.9;
            document.getElementById("n").value=30;
            document.getElementById("tau").value=0.1;
            document.getElementById("tau_slider").value=0.1;
            document.getElementById("gamma").value=1.00;
            document.getElementById("gamma_slider").value=1.00;
            document.getElementById("textbox_seeds").value = 'P63092 P35354 P01229 P01148 Q5JWF2 P84996 O95467 P05019'; // PP case study
}



$(document).on('keydown', 'input[pattern]', function(e){
  var input = $(this);
  var oldVal = input.val();
  var regex = new RegExp(input.attr('pattern'), 'g');
  setTimeout(function(){
    var newVal = input.val();
    if(!regex.test(newVal)){
      input.val(oldVal); 
    }
  }, 1);
});



$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})




function myFunction() {
  var dots = document.getElementById("dots");
  var moreText = document.getElementById("more");
  var btnText = document.getElementById("myBtn");

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Read more"; 
    moreText.style.display = "none";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Read less"; 
    moreText.style.display = "inline";
  }
}





$("#alpha").on("blur", function () {
    if ($(this).val().trim().length == 0) {
        $(this).val("0");
        $("#alpha_slider").val("0");
    }
});
//trigger blur once for the initial setting:
$("#alpha").trigger("blur");

$("#beta").on("blur", function () {
    if ($(this).val().trim().length == 0) {
        $(this).val("0");
        $("#beta_slider").val("0");
    }
});
//trigger blur once for the initial setting:
$("#beta").trigger("blur");

$("#tau").on("blur", function () {
    if ($(this).val().trim().length == 0) {
        $(this).val("0");
        $("#tau_slider").val("0");
    }
});
//trigger blur once for the initial setting:
$("#tau").trigger("blur");

$("#gamma").on("blur", function () {
    if ($(this).val().trim().length == 0) {
        $(this).val("0");
        $("#gamma_slider").val("0");
    }
});
//trigger blur once for the initial setting:
$("#gamma").trigger("blur");


$('[data-toggle="popover"]').popover();

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

const button = document.getElementById('myButton')
const value = document.getElementById('myValue')
const progressbar = document.getElementById('myProgress')

function update_bar(value) {
  progressbar.setAttribute("aria-valuenow", value);
  progressbar.style.width = value + '%';

  // progress bar should have label
  progressbar.innerHTML = value + '%';
}

button.addEventListener('click', function(e) {

  // Reset progress bar incase of re-click.
  update_bar(0);


  fetch(`${window.origin}/enqueue`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      value: value.value
    }),
  }).then((r) => {
    r.json().then((data) => {

      // The job.id returned from the server once enqueued:
      job_id = data['job_id'];

      const source = new EventSource("/progress/" + job_id);
      
      source.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log(data);

        update_bar(data['value']);

        if (data['status'] == 'finished') {

          // Manually set progress to 100 when job is finished, as
          // actual progress value may be less from last read.

          update_bar(100);

          source.close();

          // Just write the result which is included in the last streamed item
          // to the page
          document.getElementById('result').textContent = data['result'];
        }
      }

    })
  });

});











var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}


var coll_edge_params = document.getElementsByClassName("collapsible_edge_params");
var i;

for (i = 0; i < coll_edge_params.length; i++) {
    coll_edge_params[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    } 
  });
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

















  // P_value