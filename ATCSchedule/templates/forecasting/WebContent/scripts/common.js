
var table = undefined;
var columnCount = undefined;
function createTableObj(tableBorder,tableId,tablestyle){
	 if(document.getElementById(tableId) == null){
		 table = document.createElement("TABLE");
		 table.border = tableBorder;
		 table.classList.add(tablestyle);
		 table.id = tableId;
	 }
	
}

function getTableLength(tableId){
	if(document.getElementById(tableId) == null){
		return 0;
	}
	var oRows = document.getElementById(tableId).getElementsByTagName('tr');
	var iRowCount = oRows.length;
	return iRowCount
}


function createHeader(jsonObj){
	 //Get the count of columns.
  columnCount = jsonObj[0].length;

  //Add the header row.
  row = table.insertRow(-1);
  for (var i = 0; i < columnCount; i++) {
      var headerCell = document.createElement("TH");
      headerCell.innerHTML = jsonObj[0][i];
      headerCell.classList.add('wordwrap');
      row.appendChild(headerCell);
     
  }
}

function createSpanHeader(jsonObj){
	 //Get the count of columns.
 columnCount = jsonObj[0].length;

 //Add the header row.
 var row = table.insertRow(-1);
 for (var i = 0; i < columnCount; i++) {
     var headerCell = document.createElement("TH");
     headerCell.innerHTML = jsonObj[0][i];
     if(i >1){
     	headerCell.colSpan = 2;
     }
     if(i < 2){
     	headerCell.rowSpan = 2;
     }
     headerCell.classList.add('wordwrap');
     row.appendChild(headerCell);
    
 }
}
/*
function createButtonForCell(cell,btnName,btnId){
    
    // creating button element
    var button = document.createElement('BUTTON');
     
    // creating text to be
    //displayed on button
    var text = document.createTextNode(btnName);
     
    // appending text to button
    button.appendChild(text);
    button.id=btnId; 
    button.addEventListener("click", function() {
    	console.log("hello");
    },false);
    // appending button to div
    cell.appendChild(button); ;
}

function createButton(parentId,btnName,btnId){
	var btnParent = document.getElementById(parentId);
    
    // creating button element
    var button = document.createElement('BUTTON');
     
    // creating text to be
    //displayed on button
    var text = document.createTextNode(btnName);
     
    // appending text to button
    button.appendChild(text);
   // button.attributes("id",btnId);
    // appending button to div
    btnParent.appendChild(button); ;
}
*/


