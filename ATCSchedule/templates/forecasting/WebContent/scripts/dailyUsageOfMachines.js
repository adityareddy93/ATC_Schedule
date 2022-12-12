function getDailyUsageOfMahines(divId){
	 //Build an array containing Customer records.
    var dailyUsageOfMachines = new Array();
    dailyUsageOfMachines.push([ "Machine", "Insert","Tim","Comments"]);
    dailyUsageOfMachines.push(["Milling 1", "700","510","620"]);
    dailyUsageOfMachines.push([ "Milling 2", "700","510","620"]);
    dailyUsageOfMachines.push([ "EDM 1", "700","510","620"]);
    generateTable(dailyUsageOfMachines,"0","Add Insert","dailyUsgMachines",divId);
    //generateTable(estimatedHours,"0","Add Insert","estmatedHrId",divId);
}
function generateTable(jsonObj,tableBorder,btnName,btnId,divId) {
	 createTableObj(tableBorder,"inputTblId",'tablestyle');
	 createHeader(jsonObj);
	 createDailyUsageOfMachines(jsonObj,btnName,btnId,divId,true,true);   
    }

function createDailyUsageOfMachines(jsonObj,btnName,btnId,divId,clrTable,btnReq){
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

function addInsert(){
	var tableRows = getTableLength('inputTblId') - 1 ; 
//	alert('Your table has ' + tableRows + ' rows.');
	var newRow = table.insertRow(tableRows);
	for (var j = 0; j < columnCount; j++) {
		var cell = newRow.insertCell(-1);
		if (j == 0) {
			cell.innerHTML = tableRows;
		} else {
			cell.innerHTML = "<input type='text' name='"+ "name".concat(tableRows) + "' value=''>";
		}

	}
}