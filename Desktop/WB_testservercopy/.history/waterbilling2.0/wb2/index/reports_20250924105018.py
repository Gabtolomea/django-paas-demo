from collections import defaultdict
import calendar
from calendar import month_name
from datetime import datetime
import openpyxl
from openpyxl.styles import Font
from django.shortcuts import render
from django.http import HttpResponse
from .models import ConsumerInfo, Transactions
from .views import *

#Created this 24th of March 2025 -- Kathrina D. Bandajon

from datetime import datetime
import calendar
from collections import defaultdict

@login_required(login_url='login')
def monthly_billing_report(request):
    start_month = int(request.GET.get("start_month", 4))
    start_year = int(request.GET.get("start_year", 2024))
    end_month = int(request.GET.get("end_month", 2))
    end_year = int(request.GET.get("end_year", 2025))

    # Build start and end datetime objects
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    # Get all transactions within the date range with Billing type
    transactions = Transactions.objects.filter(
        transType="Billing",
        year__gte=start_date.year,
        year__lte=end_date.year,
    ).select_related("acctID")

    # Optional: further reduce queryset with precise filtering
    transactions = [
        t for t in transactions
        if start_date <= datetime(t.year, t.month, 1) <= end_date
    ]

    consumer_data = defaultdict(lambda: defaultdict(float))
    months_set = set()

    for trans in transactions:
        consumer = trans.acctID
        if not consumer:
            continue

        consumer_name = f"{consumer.lastname}, {consumer.firstname}".strip()
        bill_month = datetime(trans.year, trans.month, 1)
        month_label = f"{calendar.month_abbr[trans.month]} - {str(trans.year)[-2:]}"
        consumer_data[consumer_name][month_label] += round(float(trans.bill or 0), 2)
        months_set.add(month_label)

    # Sort months chronologically
    months_list = sorted(months_set, key=lambda x: datetime.strptime(x, "%b - %y"))

    # Sort consumers by name
    sorted_consumers = sorted(consumer_data.keys())
    table_data = [
        [consumer] + [f"₱{consumer_data[consumer].get(month, 0):,.2f}" for month in months_list]
        for consumer in sorted_consumers
    ]

    total_row = ["Total"] + [
        f"₱{sum(consumer_data[c][month] for c in consumer_data):,.2f}" for month in months_list
    ]

    if "export" in request.GET:
        return generate_excel(months_list, table_data, total_row)

    months_n = [(i, month_name[i]) for i in range(1, 13)] 
    months_range = range(1, 13)  # 1 to 12
    years_range = range(2020, datetime.now().year + 2)  # or customize

    return render(request, "billreportcopy.html", {
        "months_list": months_list,
        "months_n": months_n,
        "table_data": table_data,
        "total_row": total_row,
        "start_month": start_month,
        "start_year": start_year,
        "end_month": end_month,
        "end_year": end_year,
        "months_range": months_range,
        "years_range": years_range,
        "cur_year": datetime.now().year,
        'is_mbr': True,
    })


def clean_string(value):
    if isinstance(value, str):
        return ILLEGAL_CHARACTERS_RE.sub('', value)
    return value

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


