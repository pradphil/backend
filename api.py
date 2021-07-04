import sqlite3
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True



def createresponse(customers, total_discount_amount, items,
                   order_total_avg, discount_rate_avg,
                   comm_total, comm_order_average, comm_promotions):
    resp = {}
    promotions = {}
    commissiondata = {}

    resp["customers"] = customers
    resp["total_discount_amount"] = total_discount_amount
    resp["items"] = items
    resp["order_total_avg"] = order_total_avg
    resp["discount_rate_avg"] = discount_rate_avg

    commissiondata["total"] = comm_total
    commissiondata["order_average"] = comm_order_average
    commissiondata["promotions"] = comm_promotions

    resp["commissions"] = commissiondata

    return resp

def queryanalyticsondate(datestring):
    '''
    :param datestring:eg 2019-08-01
    :return: dictionary that is of desired output
    Creates a dictionary that is source of response that is returned as json
    '''

    conn = sqlite3.connect('test.db')
    print("Opened database successfully")

    sql_customercount = "SELECT * FROM orders WHERE created_at like \"%{dateforsql}%\"".format(dateforsql=datestring)
    print(sql_customercount)
    sql_cursor= conn.execute(sql_customercount)
    customers = sql_cursor.fetchall()
    customercount = len(customers)
    totalitems = 0
    sum_fullamount = 0
    sum_discountamount = 0
    totaldiscount = 0
    sum_orderttotal = 0
    avgordertotal = 0
    for row in customers:
        sql_itemsinorder = "SELECT * FROM order_lines WHERE order_id = {order_idis}".format(order_idis=row[0])
        print(sql_itemsinorder)
        sql_cursor = conn.execute(sql_itemsinorder)
        fetcheditems = sql_cursor.fetchall()
        print(len(fetcheditems))
        totalitems = totalitems + len(fetcheditems)

        sql_sumfullamount = "SELECT SUM(full_price_amount)FROM order_lines WHERE  order_id = {order_idis}".format(order_idis=row[0])
        print(sql_sumfullamount)
        sql_cursor = conn.execute(sql_sumfullamount)
        sum_fullamount += sql_cursor.fetchone()[0]

        sql_sumdiscountamount = "SELECT SUM(discounted_amount)FROM order_lines WHERE  order_id = {order_idis}".format(order_idis=row[0])
        print(sql_sumdiscountamount)
        sql_cursor = conn.execute(sql_sumdiscountamount)
        sum_discountamount += sql_cursor.fetchone()[0]

        sql_sumorderttotal = "SELECT SUM(total_amount)FROM order_lines WHERE  order_id = {order_idis}".format(order_idis=row[0])
        print(sql_sumorderttotal)
        sql_cursor = conn.execute(sql_sumorderttotal)
        sum_orderttotal += sql_cursor.fetchone()[0]


    totaldiscount = sum_fullamount - sum_discountamount
    if( customercount > 0 ):
        avgordertotal = sum_orderttotal / customercount

    retresp = createresponse( customers= customercount, total_discount_amount = totaldiscount, items = totalitems,
                    order_total_avg = avgordertotal, discount_rate_avg = "pending",
                    comm_total = "pending", comm_order_average = "pending", comm_promotions ={})

    print("Operation done successfully")

    conn.close()

    return retresp

def validatedatestring(datestring):
    '''
    :param datestring:  eg: 20190801
    :return: True or False
    Checks basic date validation for length
    '''
    if ( len(datestring) != 8):
        return False
    else:
        return True

def getformateddatestring(datestring):
    '''
    :param datestring: eg: 20190801
    :return: string in format 2019-08-01
    Returns string in format that is useful for sql query
    '''
    yearis = datestring[:4]
    monthis = datestring[4:6]
    dayis = datestring[6:8]

    return("-".join([yearis, monthis, dayis]))


@app.route('/api/v1/analytics', methods=['GET'])
def api_id():
    '''
    :return: json of desired output
    Check if a date was provided as part of the URL and creates json response
    '''

    if 'date' in request.args:
        dateis = request.args['date']
        if(validatedatestring(dateis)):
            resp = queryanalyticsondate(getformateddatestring(dateis))
        else:
            return "Error: Invalid date string"
    else:
        return "Error: No date field provided. Please specify a date."

    return jsonify(resp)

app.run()