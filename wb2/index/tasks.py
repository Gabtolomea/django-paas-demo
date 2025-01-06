from background_task import background
from datetime import datetime, timedelta
from .models import *

#added by K. Bandajon October 29, 2024 The new penalty rate-.- ID: NewPenaltyOct2024
#@background(schedule=0)
def new_penalty_rate():
    nowDate = datetime.today()
    PrevMonth = 12 if nowDate.month == 1 else nowDate.month - 1
    print(PrevMonth)
    #Year = nowDate.year + 1 if nowDate.month == 1 else now.year 
    newRate_penalty = .20
    allConsumers = ConsumerInfo.objects.all()

    for consumers in allConsumers:
            #print(consumers)
            forPenalty = Transactions.objects.filter(
                    month = PrevMonth,
                    year = nowDate.year,
                    acctID = consumers.consumer_id,
                    transType= "Billing",
                    is_billpaid = False,
                    ).first()
            #print(f"{consumers.consumer_id} {forPenalty}")


            if forPenalty is not None:
                ifPenaltyExists = Transactions.objects.filter(
                        acctID=consumers,
                            transType="Penalty",
                            usage=None, 
                            month=PrevMonth,
                            year=nowDate.year,
                            processedBy="System",
                ).exists()
                
                if ifPenaltyExists:
                    print(f"{consumers.consumer_id} {forPenalty} It  exist")
                    pass
                else:
                    penalty_bill = forPenalty.bill * newRate_penalty
                    print(penalty_bill)
                        
                    penalty_transaction = Transactions(
                        acctID=consumers,
                        transType="Penalty",
                        usage=None, 
                        contypeid=consumers.contypeid,
                        bill=penalty_bill,
                        month=PrevMonth,
                        year=nowDate.year,
                        processedBy="System",
                        date = nowDate,
                    )
                    try:
                        penalty_transaction.save()
                        print(f"New penalty rate applied on {datetime.now()}.")
                    except Exception as e:
                        print(f"Error saving transaction: {e}")
            else:
                #print(f"No unpaid bill transactions found for consumer ID {consumers.consumer_id}.")
                pass
    
@background(schedule=5) #replace 86400 - seconds to make it run in every 24hours
def schedule_monthlyTask():
    today = datetime.now()
    if today.day == 19:
        new_penalty_rate()
    else:
        next_run = (today.replace(day=1) + timedelta(days=31)).replace(day=19)
        print(next_run)
        #new_penalty_rate()

schedule_monthlyTask()