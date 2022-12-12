function showTotalLoadSystemReportDetails(divId) {
	var totalLoadSysReport = new Array();
	totalLoadSysReport.push(["", "Tool Information", "Machining Completion Date (Ideal Case)","Machining Completion Date (Worst Case)",]);
	totalLoadSysReport.push(["1","2002", "Nov 10th","Nov 20th"]);
	totalLoadSysReport.push(["2", "2027", "December 15th","December 25th"]);
	totalLoadSysReport.push(["3", "-----", "--------","----"]);	
	generateTable(totalLoadSysReport,"1",divId);
}



function generateTable(jsonObj,tableBorder,divId) {
	   createTableObj(tableBorder,"inputTblId");
	   createHeader(jsonObj);
	   createTotalLoadSystemReportTableBody(jsonObj,divId,true);
}

function setTableToDiv(clrTable,divId){
	var dvTable = document.getElementById(divId);
	if(clrTable)
		dvTable.innerHTML = "";
	dvTable.appendChild(table);
}


function createTotalLoadSystemReportTableBody(jsonObj,divId,clrTable){
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
	setTableToDiv(clrTable,divId);
}
