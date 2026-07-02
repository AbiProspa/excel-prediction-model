import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "outputs/feedback_dataset";

const headers = [
  "Date",
  "Customer",
  "Feedback Type",
  "Rating (1-5)",
  "Status",
  "Follow-Up",
  "Comments",
];

const rows = [
  ["2025-04-25", "Customer 1", "Service", 5, "Resolved", "No", "Very helpful and polite staff"],
  ["2025-06-24", "Customer 2", "Loan Process", 4, "Resolved", "No", "Clear loan steps"],
  ["2025-05-22", "Customer 3", "Service", 5, "Resolved", "No", "Very helpful and polite staff"],
  ["2025-06-20", "Customer 4", "Online Banking", 2, "Not Resolved", "Yes", "Frequent login errors"],
  ["2025-05-19", "Customer 5", "Service", 4, "Resolved", "No", "Good customer service"],
  ["2025-05-04", "Customer 6", "ATM", 4, "Resolved", "No", "Quick withdrawal, slight delay"],
  ["2025-04-04", "Customer 7", "Service", 3, "Resolved", "No", "Average service experience"],
  ["2025-06-02", "Customer 8", "App", 4, "Resolved", "No", "Good app performance"],
  ["2025-05-04", "Customer 9", "Loan Process", 3, "Not Resolved", "Yes", "Process was manageable"],
  ["2025-04-05", "Customer 10", "Service", 3, "Not Resolved", "Yes", "Support eventually helped"],
  ["2025-04-22", "Customer 11", "Loan Process", 5, "Resolved", "No", "Excellent loan experience"],
  ["2025-06-27", "Customer 12", "Loan Process", 5, "Resolved", "No", "Excellent loan experience"],
  ["2025-04-18", "Customer 13", "Loan Process", 3, "Not Resolved", "Yes", "Loan took longer than expected"],
  ["2025-06-05", "Customer 14", "ATM", 4, "Resolved", "No", "ATM works most of the time"],
  ["2025-04-15", "Customer 15", "Online Banking", 5, "Resolved", "No", "Excellent online banking"],
  ["2025-05-22", "Customer 16", "App", 3, "Resolved", "No", "Works fine with small issues"],
  ["2025-06-14", "Customer 17", "Service", 4, "Resolved", "No", "Friendly staff"],
  ["2025-06-25", "Customer 18", "Loan Process", 5, "Resolved", "No", "Excellent loan experience"],
  ["2025-06-22", "Customer 19", "Service", 3, "Not Resolved", "Yes", "Average service experience"],
  ["2025-05-23", "Customer 20", "App", 2, "Not Resolved", "Yes", "Login issues sometimes"],
  ["2025-04-29", "Customer 21", "App", 3, "Resolved", "No", "Works fine with small issues"],
  ["2025-04-29", "Customer 22", "Loan Process", 2, "Not Resolved", "Yes", "Too many requirements"],
  ["2025-06-12", "Customer 23", "App", 5, "Resolved", "No", "Excellent app experience"],
  ["2025-05-04", "Customer 24", "Online Banking", 3, "Resolved", "No", "Online banking is stable"],
  ["2025-06-19", "Customer 25", "Online Banking", 3, "Resolved", "No", "Online banking is stable"],
  ["2025-06-30", "Customer 26", "ATM", 2, "Not Resolved", "Yes", "ATM failed twice"],
  ["2025-05-10", "Customer 27", "App", 3, "Resolved", "No", "App is okay but laggy"],
  ["2025-07-01", "Customer 28", "Mobile App", 4, "Resolved", "No", "App update improved loading speed"],
  ["2025-07-02", "Customer 29", "ATM", 1, "Not Resolved", "Yes", "ATM deducted cash but did not dispense"],
  ["2025-07-03", "Customer 30", "Customer Service", 5, "Resolved", "No", "Staff handled my complaint professionally"],
  ["2025-07-04", "Customer 31", "Loan Process", 2, "Not Resolved", "Yes", "Loan approval took too long"],
  ["2025-07-05", "Customer 32", "Online Banking", 4, "Resolved", "No", "Transfer worked smoothly"],
  ["2025-07-06", "Customer 33", "Branch Experience", 3, "Resolved", "No", "Queue was long but service was okay"],
  ["2025-07-07", "Customer 34", "Debit Card", 2, "Not Resolved", "Yes", "Card was blocked without notice"],
  ["2025-07-08", "Customer 35", "Mobile App", 5, "Resolved", "No", "Very easy to check account balance"],
  ["2025-07-09", "Customer 36", "Internet Banking", 3, "Resolved", "No", "Login works but pages load slowly"],
  ["2025-07-10", "Customer 37", "POS Transaction", 1, "Not Resolved", "Yes", "Failed POS transaction not reversed"],
  ["2025-07-11", "Customer 38", "Customer Service", 4, "Resolved", "No", "Agent explained the issue clearly"],
  ["2025-07-12", "Customer 39", "ATM", 3, "Resolved", "No", "Machine worked but receipt was not printed"],
  ["2025-07-13", "Customer 40", "Loan Process", 5, "Resolved", "No", "Loan officer was very supportive"],
  ["2025-07-14", "Customer 41", "Mobile App", 2, "Not Resolved", "Yes", "App keeps closing during transfers"],
  ["2025-07-15", "Customer 42", "Account Opening", 4, "Resolved", "No", "Account was opened faster than expected"],
  ["2025-07-16", "Customer 43", "Online Banking", 5, "Resolved", "No", "Bill payment feature worked perfectly"],
  ["2025-07-17", "Customer 44", "Branch Experience", 2, "Not Resolved", "Yes", "Staff response was slow"],
  ["2025-07-18", "Customer 45", "Debit Card", 4, "Resolved", "No", "New card was issued on time"],
  ["2025-07-19", "Customer 46", "POS Transaction", 3, "Resolved", "No", "Reversal came after two days"],
  ["2025-07-20", "Customer 47", "Customer Service", 1, "Not Resolved", "Yes", "Complaint was not properly attended to"],
  ["2025-07-21", "Customer 48", "ATM", 5, "Resolved", "No", "ATM was fast and available"],
  ["2025-07-22", "Customer 49", "Mobile App", 3, "Resolved", "No", "App works but notifications delay"],
  ["2025-07-23", "Customer 50", "Loan Process", 4, "Resolved", "No", "Loan requirements were clearly explained"],
  ["2025-07-24", "Customer 51", "Internet Banking", 2, "Not Resolved", "Yes", "Password reset did not work"],
  ["2025-07-25", "Customer 52", "Account Opening", 5, "Resolved", "No", "Very smooth onboarding process"],
  ["2025-07-26", "Customer 53", "Branch Experience", 4, "Resolved", "No", "Staff were polite and helpful"],
  ["2025-07-27", "Customer 54", "Debit Card", 1, "Not Resolved", "Yes", "Card replacement request still pending"],
  ["2025-07-28", "Customer 55", "Online Banking", 3, "Resolved", "No", "Service is fair but can be faster"],
  ["2025-07-29", "Customer 56", "POS Transaction", 4, "Resolved", "No", "Issue was reversed within 24 hours"],
  ["2025-07-30", "Customer 57", "Customer Service", 5, "Resolved", "No", "Support team followed up quickly"],
  ["2025-07-31", "Customer 58", "ATM", 2, "Not Resolved", "Yes", "ATM network failed repeatedly"],
  ["2025-08-01", "Customer 59", "Mobile App", 4, "Resolved", "No", "Fingerprint login works well"],
  ["2025-08-02", "Customer 60", "Loan Process", 3, "Resolved", "No", "Process was okay but documentation was much"],
  ["2025-08-03", "Customer 61", "Internet Banking", 5, "Resolved", "No", "Easy to download bank statement"],
  ["2025-08-04", "Customer 62", "Branch Experience", 1, "Not Resolved", "Yes", "Customer waited too long without help"],
  ["2025-08-05", "Customer 63", "Debit Card", 3, "Resolved", "No", "Card works but activation was delayed"],
  ["2025-08-06", "Customer 64", "Account Opening", 2, "Not Resolved", "Yes", "KYC verification is still pending"],
  ["2025-08-07", "Customer 65", "Online Banking", 4, "Resolved", "No", "Transfer limit update was successful"],
  ["2025-08-08", "Customer 66", "POS Transaction", 2, "Not Resolved", "Yes", "Merchant debit issue unresolved"],
  ["2025-08-09", "Customer 67", "Customer Service", 4, "Resolved", "No", "Staff gave clear instructions"],
  ["2025-08-10", "Customer 68", "ATM", 3, "Resolved", "No", "ATM location was accessible but crowded"],
  ["2025-08-11", "Customer 69", "Mobile App", 5, "Resolved", "No", "App design is simple and useful"],
  ["2025-08-12", "Customer 70", "Loan Process", 1, "Not Resolved", "Yes", "No update after submitting documents"],
  ["2025-08-13", "Customer 71", "Internet Banking", 4, "Resolved", "No", "Transaction history was easy to access"],
  ["2025-08-14", "Customer 72", "Branch Experience", 5, "Resolved", "No", "Branch manager resolved my issue quickly"],
  ["2025-08-15", "Customer 73", "Debit Card", 2, "Not Resolved", "Yes", "Card was charged twice for maintenance"],
  ["2025-08-16", "Customer 74", "Account Opening", 3, "Resolved", "No", "Account setup was successful but slow"],
  ["2025-08-17", "Customer 75", "Online Banking", 1, "Not Resolved", "Yes", "Unable to complete transfer all day"],
].map((row) => [new Date(`${row[0]}T00:00:00`), ...row.slice(1)]);

await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const dataSheet = workbook.worksheets.add("Feedback Data");
const summarySheet = workbook.worksheets.add("Summary");

dataSheet.showGridLines = false;
summarySheet.showGridLines = false;

dataSheet.getRange("A1:G1").values = [headers];
dataSheet.getRange(`A2:G${rows.length + 1}`).values = rows;

const tableRange = `A1:G${rows.length + 1}`;
const table = dataSheet.tables.add(tableRange, true, "FeedbackTable");
table.showFilterButton = true;
table.showBandedRows = true;

dataSheet.freezePanes.freezeRows(1);
dataSheet.getRange("A1:G1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF" },
};
dataSheet.getRange(tableRange).format.borders = {
  preset: "outside",
  style: "thin",
  color: "#B7C9D9",
};
dataSheet.getRange(`A2:A${rows.length + 1}`).format.numberFormat = "yyyy-mm-dd";
dataSheet.getRange(`D2:D${rows.length + 1}`).format.numberFormat = "0";
dataSheet.getRange(`A1:G${rows.length + 1}`).format.wrapText = false;
dataSheet.getRange("A:A").format.columnWidth = 12;
dataSheet.getRange("B:B").format.columnWidth = 14;
dataSheet.getRange("C:C").format.columnWidth = 20;
dataSheet.getRange("D:D").format.columnWidth = 12;
dataSheet.getRange("E:E").format.columnWidth = 15;
dataSheet.getRange("F:F").format.columnWidth = 12;
dataSheet.getRange("G:G").format.columnWidth = 44;

dataSheet.getRange(`D2:D${rows.length + 1}`).dataValidation = {
  rule: { type: "whole", operator: "between", formula1: 1, formula2: 5 },
};
dataSheet.getRange(`E2:E${rows.length + 1}`).dataValidation = {
  rule: { type: "list", values: ["Resolved", "Not Resolved"] },
};
dataSheet.getRange(`F2:F${rows.length + 1}`).dataValidation = {
  rule: { type: "list", values: ["Yes", "No"] },
};

summarySheet.getRange("A1:D1").merge();
summarySheet.getRange("A1").values = [["Customer Feedback Summary"]];
summarySheet.getRange("A1:D1").format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF", size: 16 },
};
summarySheet.getRange("A3:B8").values = [
  ["Metric", "Value"],
  ["Total Feedback", null],
  ["Average Rating", null],
  ["Resolved", null],
  ["Not Resolved", null],
  ["Follow-Up Needed", null],
];
summarySheet.getRange("B4:B8").formulas = [
  [`=COUNTA('Feedback Data'!B2:B${rows.length + 1})`],
  [`=AVERAGE('Feedback Data'!D2:D${rows.length + 1})`],
  [`=COUNTIF('Feedback Data'!E2:E${rows.length + 1},"Resolved")`],
  [`=COUNTIF('Feedback Data'!E2:E${rows.length + 1},"Not Resolved")`],
  [`=COUNTIF('Feedback Data'!F2:F${rows.length + 1},"Yes")`],
];
summarySheet.getRange("A3:B3").format = {
  fill: "#D9EAF7",
  font: { bold: true, color: "#12344D" },
};
summarySheet.getRange("A3:B8").format.borders = {
  preset: "all",
  style: "thin",
  color: "#C7D7E3",
};
summarySheet.getRange("B5").format.numberFormat = "0.0";
summarySheet.getRange("A:A").format.columnWidth = 22;
summarySheet.getRange("B:B").format.columnWidth = 16;

summarySheet.getRange("D3:E13").values = [
  ["Feedback Type", "Count"],
  ["Service", null],
  ["Loan Process", null],
  ["Online Banking", null],
  ["ATM", null],
  ["App", null],
  ["Mobile App", null],
  ["Customer Service", null],
  ["Branch Experience", null],
  ["Debit Card", null],
  ["POS Transaction", null],
];
summarySheet.getRange("E4:E13").formulas = [
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D4)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D5)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D6)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D7)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D8)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D9)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D10)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D11)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D12)`],
  [`=COUNTIF('Feedback Data'!C2:C${rows.length + 1},D13)`],
];
summarySheet.getRange("D3:E3").format = {
  fill: "#D9EAF7",
  font: { bold: true, color: "#12344D" },
};
summarySheet.getRange("D3:E13").format.borders = {
  preset: "all",
  style: "thin",
  color: "#C7D7E3",
};
summarySheet.getRange("D:D").format.columnWidth = 22;
summarySheet.getRange("E:E").format.columnWidth = 12;

const dataPreview = await workbook.render({
  sheetName: "Feedback Data",
  range: "A1:G20",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/feedback_data_preview.png`, new Uint8Array(await dataPreview.arrayBuffer()));

const summaryPreview = await workbook.render({
  sheetName: "Summary",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/summary_preview.png`, new Uint8Array(await summaryPreview.arrayBuffer()));

const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(formulaErrors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/Customer_Feedback_Data.xlsx`);
console.log(`${outputDir}/Customer_Feedback_Data.xlsx`);
