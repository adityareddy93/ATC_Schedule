function showEstimatedHoursDetails(divId) {
	var estimatedHours = new Array();
	estimatedHours.push([ "", "Insert", "Milling", "EDM", "Wirecut", "......"]);
	estimatedHours.push([ 1, "Core Insert", "", "", "", "......" ]);
	estimatedHours.push([ 2, "Core Insert", "700", "510", "620", "......" ]);
  //estimatedHours.push([ 3, "Core Insert", "700", "510", "620", "......" ]);
	//showEstimatedHoursDetails1(estimatedHours);
	generateTable(estimatedHours,"0","Add Insert","estmatedHrId",divId);
}



function generateTable(jsonObj,tableBorder,btnName,btnId,divId) {
	   createTableObj(tableBorder,"inputTblId",'tablestyle');
	   createHeader(jsonObj);
	   createEstimatedHoursTableBody(jsonObj,btnName,btnId,divId,true,true);
}


function addInsert(){
	var table = document.getElementById('inputTblId');
	//alert("hello: "+columnCount+" rows: "+($(".tablestyle >tbody>tr").length-1));
	var tableRows = getTableLength('inputTblId') - 1 ; //$(".tablestyle >tbody>tr").length-1;
	//alert('Your table has ' + tableRows + ' rows.');
	var newRow = table.insertRow(tableRows);
	for (var j = 0; j < columnCount; j++) {
		//namePos = parseInt(namePos);
		var cell = newRow.insertCell(-1);
		if (j == 0) {
			cell.innerHTML = tableRows;

			//sno = parseInt(sno,1);
		} else {
			cell.innerHTML = "<input type='text' name='"+ "name".concat(tableRows) + "' value=''>";
		}

	}
}

function setTableToDiv(clrTable,btnReq,btnName,btnId,divId){
	if(btnReq){
		row = table.insertRow(-1);
		var cell = row.insertCell(-1);
		cell.innerHTML = "<input type='button' id='"+btnId+"' name='"+btnName+"' value='"+btnName+"' onclick='addInsert()'>"
	}

	var dvTable = document.getElementById(divId);
	if(clrTable)
		dvTable.innerHTML = "";
	dvTable.appendChild(table);
}


function createEstimatedHoursTableBody(jsonObj,btnName,btnId,divId,clrTable,btnReq){
	let sno =1;
	for (var i = 1; i < jsonObj.length; i++) {
		row = table.insertRow(-1);
		var namePos = 0;
		for (var j = 0; j < columnCount; j++) {
			namePos = parseInt(namePos) + 1;
			var cell = row.insertCell(-1);
			if (j == 0) {
				cell.innerHTML = sno;
				sno++;
				//sno = parseInt(sno,1);
			} else {
				cell.innerHTML = "<input type='text' name='"+ "name".concat(namePos) + "' value='"+ jsonObj[i][j] + "'>";
			}

		}
	}
	setTableToDiv(clrTable,btnReq,btnName,btnId,divId);
}

function addAnotherEstimatedHoursTableBody(divId){
	//generateTable(estimatedHours,"0","Add Insert","estmatedHrId",divId);
	var estimatedHours = new Array();
	estimatedHours.push([ "", "Insert", "Milling", "EDM", "Wirecut", "......" ]);
	estimatedHours.push([ 1, "Core Insert", "700", "510", "620", "......" ]);
	estimatedHours.push([ 2, "Core Insert", "700", "510", "620", "......" ]);
	createTableObj("0","inputTblId",'tablestyle');
	createHeader(estimatedHours);
	createEstimatedHoursTableBody(estimatedHours,"Add Insert","estmatedHrId",divId,false,true);
}

function addAnotherEstimatedHoursFinalTableBody(divId){
	var estimatedHours = new Array();
	estimatedHours.push([ "SNo", "Insert", "Milling", "EDM", "Wirecut", "......" ]);
	estimatedHours.push([ 1, "Core Insert", "700", "510", "620", "......" ]);
	estimatedHours.push([ 2, "Core Insert", "700", "510", "620", "......" ]);
	 if(document.getElementById('finalTblId') == null){
		createTableObj("1","finalTblId",'finalTblStyle');
		createHeader(estimatedHours);
	 }
	createEstimatedHoursFinalTable(estimatedHours,"Add Insert","finalEstmatedHrId",divId,false,false);

}


function createEstimatedHoursFinalTable(jsonObj,btnName,btnId,divId,clrTable,btnReq){
	let sno = getTableLength('finalTblId');//1;
	if(sno > 0){
		sno--;
	}
	var inputTable = document.getElementById('inputTblId');
	for (var i = 1; i < inputTable.rows.length-1; i++) {
		var objCells = inputTable.rows.item(i).cells;
		console.log(objCells);
		row = table.insertRow(-1);
		var namePos = 0;
		for (var j = 0; j < columnCount; j++) {
			namePos = parseInt(namePos) + 1;
			var cell = row.insertCell(-1);
			if (j == 0) {
				sno++;
				cell.innerHTML = sno;
			} else {
				cell.innerHTML = objCells[j].children[0].value;//jsonObj[i][j];
			}

		}
	}
	setTableToDiv(clrTable,btnReq,btnName,btnId,divId);
}

function submitEstimatedHoursDetails(){

}
