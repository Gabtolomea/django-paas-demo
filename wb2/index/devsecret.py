from collections import defaultdict
import calendar
from datetime import datetime
import openpyxl
from openpyxl.styles import Font
from django.shortcuts import render
from django.http import HttpResponse
from .models import ConsumerInfo, Transactions

def monthly_billing_report(request):
    # Get date range from request (or default values)
    start_month = int(request.GET.get("start_month", 4))  # Default: April
    start_year = int(request.GET.get("start_year", 2024))  # Default: 2024
    end_month = int(request.GET.get("end_month", 2))  # Default: February
    end_year = int(request.GET.get("end_year", 2025))  # Default: 2025

    # Dictionary to store data
    consumer_data = defaultdict(lambda: defaultdict(float))  # Use float to ensure decimal precision
    months_list = []

    # Fetch all consumer records
    records = ConsumerInfo.objects.all()

    for record in records:
        consumer_name = f"{record.lastname}, {record.firstname}".strip()  # Format: Last, First
        all_bills = Transactions.objects.filter(acctID=record.consumer_id, transType='Billing')

        for bill in all_bills:
            bill_date = datetime(bill.year, bill.month, 1)
            start_date = datetime(start_year, start_month, 1)
            end_date = datetime(end_year, end_month, 1)

            if start_date <= bill_date <= end_date:
                month_year = f"{calendar.month_abbr[bill.month]} - {str(bill.year)[-2:]}"  # "Apr - 24"
                
                # Ensure the bill amount is rounded to two decimal places
                consumer_data[consumer_name][month_year] += round(float(bill.bill or 0), 2)

                if month_year not in months_list:
                    months_list.append(month_year)

    # Sort months for correct order
    months_list.sort(key=lambda x: datetime.strptime(x, "%b - %y"))

    # Prepare data for HTML template (sorted alphabetically by last name)
    sorted_consumers = sorted(consumer_data.keys())  # Sort consumers by name
    table_data = [
        [consumer] + [f"₱{consumer_data[consumer].get(month, 0):,.2f}" for month in months_list]
        for consumer in sorted_consumers
    ]

    # Calculate totals
    total_row = ["Total"] + [f"₱{sum(consumer_data[c][month] for c in consumer_data):,.2f}" for month in months_list]

    # Check if user requested an Excel file
    if "export" in request.GET:
        return generate_excel(months_list, table_data, total_row)

    return render(request, "billreportcopy.html", {"months_list": months_list, "table_data": table_data, "total_row": total_row})

def generate_excel(months_list, table_data, total_row):
    """Generate and return an Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Billing Report"

    # Add headers
    header = ["Consumer Names"] + months_list
    ws.append(header)
    for col in range(1, len(header) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    # Add consumer data
    for row in table_data:
        ws.append([row[0]] + [float(row[i][1:].replace(",", "")) for i in range(1, len(row))])  # Convert ₱ back to number

    # Add total row
    ws.append([total_row[0]] + [float(total_row[i][1:].replace(",", "")) for i in range(1, len(total_row))])

    # Format as currency in Excel
    peso_format = '"₱"#,##0.00'  # Peso format for Excel
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=len(months_list) + 1, max_row=ws.max_row):
        for cell in row:
            cell.number_format = peso_format

    # Prepare response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Billing_Report.xlsx"'
    wb.save(response)
    return response






def average_consumption_all_report(request):
    # Get date range from request (or default values)
    start_month = int(request.GET.get("start_month", 2))  # Default: April
    start_year = int(request.GET.get("start_year", 2024))  # Default: 2024
    end_month = int(request.GET.get("end_month", 2))  # Default: February
    end_year = int(request.GET.get("end_year", 2025))  # Default: 2025

    # Dictionary to store data
    consumer_data = defaultdict(lambda: defaultdict(float))  # Use float to ensure decimal precision
    months_list = []

    # Fetch all consumer records
    #records = ConsumerInfo.objects.exclude(firstname__icontains='School').exclude(lastname__icontains='School')
    #records = ConsumerInfo.objects.filter(contypeid = "C001")
    records = ConsumerInfo.objects.filter(contypeid = "C002")

    for record in records:
        consumer_name = f"{record.lastname}, {record.firstname}".strip()  # Format: Last, First
        all_usage = Transactions.objects.filter(acctID=record.consumer_id, transType='Billing')

        for usage in all_usage:
            usage_date = datetime(usage.year, usage.month, 1)
            start_date = datetime(start_year, start_month, 1)
            end_date = datetime(end_year, end_month, 1)

            if start_date <= usage_date <= end_date:
                month_year = f"{calendar.month_abbr[usage.month]} - {str(usage.year)[-2:]}"  # "Apr - 24"
                
                # Ensure the usage amount is rounded to two decimal places
                consumer_data[consumer_name][month_year] += round(float(usage.usage or 0), 2)

                if month_year not in months_list:
                    months_list.append(month_year)

    # Sort months for correct order
    months_list.sort(key=lambda x: datetime.strptime(x, "%b - %y"))

    # Prepare data for HTML template (sorted alphabetically by last name)
    sorted_consumers = sorted(consumer_data.keys())  # Sort consumers by name
    table_data = [
        [consumer] + [f"{consumer_data[consumer].get(month, 0):,.2f} m³" for month in months_list]
        for consumer in sorted_consumers
    ]

    # Calculate totals and averages
    total_row = ["Total"] + [f"{sum(consumer_data[c][month] for c in consumer_data):,.2f} m³" for month in months_list]
    avg_row = ["Average"] + [f"{(sum(consumer_data[c][month] for c in consumer_data) / len(consumer_data) if consumer_data else 0):,.2f} m³" for month in months_list]

    # Check if user requested an Excel file
    if "export" in request.GET:
        return generate_excelave1(months_list, table_data, total_row, avg_row)

    return render(request, "aveconsumption.html", {"months_list": months_list, "table_data": table_data, "total_row": total_row, "avg_row": avg_row})

def generate_excelave1(months_list, table_data, total_row, avg_row):
    """Generate and return an Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Billing Report"

    # Add headers
    header = ["Consumer Names"] + months_list
    ws.append(header)
    for col in range(1, len(header) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    # Add consumer data
    for row in table_data:
        ws.append([row[0]] + [float(row[i].replace(" m³", "").replace(",", "")) for i in range(1, len(row))])

    # Add total and average rows
    ws.append([total_row[0]] + [float(total_row[i].replace(" m³", "").replace(",", "")) for i in range(1, len(total_row))])
    ws.append([avg_row[0]] + [float(avg_row[i].replace(" m³", "").replace(",", "")) for i in range(1, len(avg_row))])

    # Prepare response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    #response["Content-Disposition"] = 'attachment; filename="All_Average_Except_School_Report.xlsx"'
    response["Content-Disposition"] = 'attachment; filename="Average_Filter_By_Commercial.xlsx"'
    wb.save(response)
    return response
