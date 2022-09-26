// "[data-action=action-pdf]".click(function () {

// var pdf = new jsPDF('p', 'pt', 'letter');
//  pdf.addHTML($('#printme')[0], function () {
//      pdf.save('Test.pdf');
 
//  });



// $('#getcopy').click(
//     function downloadClickfunction () {
// var doc = new jsPDF();
// var elementHTML = $('#dtBasicExample').html();
// var specialElementHandlers = {
//     '#ahh': function (element, renderer) {
//         return true;
//     }
// };
// doc.fromHTML(elementHTML, 15, 15, {
//     'width': 170,
//     'elementHandlers': specialElementHandlers
// });

    
// // Save the PDF
// doc.save('sample-document.pdf');
//     }
// );

// $(function () {

//     var specialElementHandlers = {

//         '#printme': function (element,renderer) {

//             return true;

//         }

//     };

// });

//  $('#getcopy').click(function () {

//         var doc = new jsPDF();

//         doc.fromHTML(

//             $('#printme').html(), 15, 15, 

//             { 'width': 170, 'elementHandlers': specialElementHandlers }, 

//             function(){ doc.save('Acount-Ledger.pdf'); }

//         );

//     });  
// $("#getcopy").live("click", function () {
//     var printDoc = new jsPDF();
//     printDoc.fromHTML($('#printme').get(0), 10, 10, {
//         'width': 180
//     });
//     printDoc.autoPrint();
//     printDoc.output("dataurlnewwindow");

// });

// var createPDFBtn = document.querySelector("[data-action=action-pdf]");
// createPDFBtn.addEventListener("click", function (event) {
//     var doc = new jsPDF("l", "pt", "a4");
  
//     doc.html(document.getElementById("printme"), {
//       callback: function (doc) {
//         doc.save("Acount-Ledger.pdf");
//       },
//       x: 10,
//       y: 10,
//     });
//   });

function getpdf() {
  const { jsPDF } = window.jspdf;

  var doc = new jsPDF('l', 'mm', [1200, 1810]);
  var pdfjs = document.querySelector('#printme');

  doc.html(pdfjs, {
      callback: function(doc) {
          doc.save("output.pdf");
      },
      x: 10,
      y: 10
  });

  doc.output('dataurlnewwindow');
}
