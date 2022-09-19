
BILL_TX_CODE = 1
PAYMENT_TX_CODE = 2


class BillingLedger:
   trans_datetime = ""
   meternumber = ""
   account_number = ""
   prev_reading = " "
   cur_reading = " "
   cu_meter = " "
   amt_billed = " "
   amt_paid = " "
   processed_by = ""
   or_number = ""
   current_balance = 0.0
   # set to 1 if bill, 2 if payment
   record_flag = BILL_TX_CODE
 
 
   def adjustbalance(self, runningbalance):
    if(self.record_flag == BILL_TX_CODE):
        self.current_balance = runningbalance + self.amt_billed
        # print('hellobilled')
    elif(self.record_flag == PAYMENT_TX_CODE):
        self.current_balance = runningbalance - self.amt_paid
        # print('hellopaid')
    return self.current_balance
   
 
   def setprev_reading(self, previousreading):
    if self.record_flag == BILL_TX_CODE:
        self.prev_reading = previousreading
       
 