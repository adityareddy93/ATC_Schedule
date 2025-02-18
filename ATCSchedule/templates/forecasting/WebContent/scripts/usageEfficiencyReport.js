function getUsageEfficiencyReport(divId) {
	var usageEfficiencyRpt = new Array();
	usageEfficiencyRpt.push(["", "Tool Information", "Milling(Hours)","EDM(Hours)", "Wirecut(Hours)"]);
	usageEfficiencyRpt.push([ "Planned","Actual", "Planned","Actual","Planned","Actual"]);
	usageEfficiencyRpt.push(["1","2002","300", "300","180","200","60","50"]);
	usageEfficiencyRpt.push(["2","2027","300", "300","180","200","60","50"]);
	usageEfficiencyRpt.push(["3", "---", "----","---","---", "----","---","---"]);
	generateTable(usageEfficiencyRpt,"1",divId);
}


function generateTable(jsonObj,tableBorder,divId) {
	   createTableObj(tableBorder,"inputTblId",'tablestyle');
	   createSpanHeader(jsonObj);
	   createUsageEfficiencyReportTableBody(jsonObj,divId,true);
}


function setTableToDiv(clrTable,divId){
	var dvTable = document.getElementById(divId);
	if(clrTable)
		dvTable.innerHTML = "";
	dvTable.appendChild(table);
}

function createUsageEfficiencyReportTableBody(jsonObj,divId,clrTable) { 
    //Build an array containing Customer records.
	//alert("createUsageEfficiencyReportTableBody");
  /*  var jsonObj = new Array();
    jsonObj.push(["", "Tool Information", "Milling(Hours)","EDM(Hours)", "Wirecut(Hours)"]);
    jsonObj.push([ "Planned","Actual", "Planned","Actual","Planned","Actual"]);
    jsonObj.push(["1","2002","300", "300","180","200","60","50"]);
    jsonObj.push(["2","2027","300", "300","180","200","60","50"]);
    jsonObj.push(["3", "---", "----","---","---", "----","---","---"]);
   

    //Create a HTML Table element.
    var table = document.createElement("TABLE");
    table.border = "1";
    table.classList.add('tablestyle');*/
 
    var columnCount = jsonObj[1].length;
   
	var spancount = 0;
    //Add the data rows.
    for (var i = 1; i < jsonObj.length; i++) {
        row = table.insertRow(-1);
        if(i==2){
      	   spancount = 2;
         }
        for (var j = 0; j < columnCount+spancount; j++) {
            var cell = row.insertCell(-1);
          	console.log(" "+jsonObj[i][j]);
          	
          	if(j==0){
        	   cell.innerHTML = jsonObj[i][j];        	  
        	   //cell.colspan = 2;
           	}else{
        	   cell.innerHTML = jsonObj[i][j];  
           }
           
        }
    }
    setTableToDiv(clrTable,divId);
//     row = table.insertRow(-1);
//     var cell = row.insertCell(-1);
//     cell.innerHTML = "<input type='button' name='click' value='Add Insert'>"
//    var dvTable = document.getElementById("dvTable");
//    dvTable.innerHTML = "";
//    dvTable.appendChild(table);
}