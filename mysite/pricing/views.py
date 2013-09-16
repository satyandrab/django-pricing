# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from lxml import html
import re
import urllib2
from django.http import Http404
from django.http import HttpResponse
from models import data
from django.core.context_processors import csrf
from xlwt import Workbook
from xlwt import easyxf
import xlwt
import datetime

def index(request):
    context = {'results': None}

    return render_to_response('pricing/index.html', context)

def refresh(request):
    entries = data.objects.all()
    count = 0
    total_price = 0.00
    for entry in entries:
        
        u = entry.ncchomelearning_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                ncc_price = price[0].replace('Now:','').strip().replace(u'\xa3','')
                entry.ncchomelearning_price = ncc_price
                count += 1
                total_price += float(ncc_price)
        
        
        u = entry.mydistance_learning_college_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            
            deal_price = parsed_src.xpath("//div[@class='ourpricevalue']/span/text()")
            if deal_price:
                price = deal_price
            else:
                price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                count += 1
                mydis_price = price[0].replace(u'\xa3','').strip()
                total_price += float(mydis_price)
                entry.mydistance_learning_college_price = mydis_price
            
        u = entry.distance_learning_centre_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                count += 1
                dis_learn_centre_price = price[0].replace(u'\xa3','')
                total_price += float(dis_learn_centre_price)
                entry.distance_learning_centre_price = dis_learn_centre_price
        
        u = entry.openstudycollege_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            
            price = parsed_src.xpath("//span[@id='fullpaymentprice']/text()")
            if price:
                openstudycollege_price = price[0].replace(u'\xa3','')
                entry.openstudycollege_price = openstudycollege_price
                count += 1
                total_price += float(openstudycollege_price)
        
        u = entry.ukopencollege_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//option[contains(text(),'Pay in Full')]/text()")
            if price:
                ukopencollege_price = price[0].rsplit(' ',1)[-1].replace(u'\xa3','')
                entry.ukopencollege_price = ukopencollege_price
                count += 1
                total_price += float(ukopencollege_price)
        
        u = entry.edistancelearning_url
        if u != '':
            op = urllib2.urlopen(u)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//td[contains(text(),'Enrolment Fee')]/following-sibling::td[1]/text()")
            if price:
                edistancelearning_price = price[0].replace(u'\xa3','')
                edistancelearning_price_discounted = (float(edistancelearning_price)*20)/100
                edistancelearning_price_actual = float(edistancelearning_price)-float(edistancelearning_price_discounted)
                entry.edistancelearning_price = edistancelearning_price_actual
                count += 1
                total_price += float(edistancelearning_price_actual)
        if count!=0:
            entry.avg_comp_price = "%.2f" %(float(total_price/count))
        else:
            entry.avg_comp_price = "0.00"
    
        entry.save()
    
    result_saved = "All prices values have been refreshed."
    context = {'result_saved': result_saved,
               'query_data': data.objects.all()}
    
    return render_to_response('pricing/index.html', context,
                              context_instance=RequestContext(request))

def delete_entry(request):
    row_id = request.GET['id']
    entry = data.objects.get(pk=row_id)
    
    entry.delete()
    list(request)
    context = {'query_data': data.objects.all()}

    return render_to_response('pricing/index.html', context,
                              context_instance=RequestContext(request))


def export(request):
    title = request.GET['title_unique']
    
    title_export = data.objects.get(title = title)
    
    book = Workbook(encoding='utf-8')
    sheet1 = book.add_sheet('Sheet 1')
    book.add_sheet('Sheet 2')
    
    header = ['Title','ncchomelearning.co.uk','mydistance-learning-college.com',
              'distance-learning-centre.co.uk','openstudycollege.com',
              'ukopencollege.co.uk','edistancelearning.co.uk','Competitor Avg. price']
    for i in range(8):
        sheet1.write(0, i, header[i], xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;'))
    
    sheet1.write(1, 0, title_export.title)
    
    if title_export.ncchomelearning_price.strip() !="":
        sheet1.write(1, 1, u'£'+title_export.ncchomelearning_price)
    else:
        sheet1.write(1, 1, '')
        
    style_less = xlwt.easyxf('pattern: pattern solid, fore_colour rose;'
                             'alignment: horiz center;'
                              'borders: left thin, right thin, top thin, bottom thin;')
    style_more = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;'
                             'alignment: horiz center;'
                             'borders: left thin, right thin, top thin, bottom thin;')
    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.mydistance_learning_college_price.strip() != "": 
            if float(title_export.ncchomelearning_price) <= float(title_export.mydistance_learning_college_price):
                sheet1.write(1, 2, u'£'+title_export.mydistance_learning_college_price, style_more)
            else:
                sheet1.write(1, 2, u'£'+title_export.mydistance_learning_college_price, style_less)
    else:
        sheet1.write(1, 2, u'£'+title_export.mydistance_learning_college_price, style_less)
        
    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.distance_learning_centre_price.strip() != "":
            if float(title_export.ncchomelearning_price) <= float(title_export.distance_learning_centre_price):
                sheet1.write(1, 3, u'£'+title_export.distance_learning_centre_price, style_more)
            else:
                sheet1.write(1, 3, u'£'+title_export.distance_learning_centre_price, style_less)
    else:
        sheet1.write(1, 3, u'£'+title_export.distance_learning_centre_price, style_less)
    
    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.openstudycollege_price.strip() != "":
            if float(title_export.ncchomelearning_price) <= float(title_export.openstudycollege_price):
                sheet1.write(1, 4, u'£'+title_export.openstudycollege_price, style_more)
            else:
                sheet1.write(1, 4, u'£'+title_export.openstudycollege_price, style_less)
    else:
        sheet1.write(1, 4, u'£'+title_export.openstudycollege_price, style_less)
        
    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.ukopencollege_price.strip() != "":
            if float(title_export.ncchomelearning_price) <= float(title_export.ukopencollege_price):
                sheet1.write(1, 5, u'£'+title_export.ukopencollege_price, style_more)
            else:
                sheet1.write(1, 5, u'£'+title_export.ukopencollege_price, style_less)
    else:
        sheet1.write(1, 5, u'£'+title_export.ukopencollege_price, style_less)
    
    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.edistancelearning_price.strip() != "":
            if float(title_export.ncchomelearning_price) <= float(title_export.edistancelearning_price):
                sheet1.write(1, 6, u'£'+title_export.edistancelearning_price, style_more)
            else:
                sheet1.write(1, 6, u'£'+title_export.edistancelearning_price, style_less)
    else:
        sheet1.write(1, 6, u'£'+title_export.edistancelearning_price, style_less)

    if title_export.ncchomelearning_price.strip() != '':
        if title_export.ncchomelearning_price.strip() !="" and title_export.mydistance_learning_college_price.strip() != "":
            if float(title_export.ncchomelearning_price) <= float(title_export.avg_comp_price):
                sheet1.write(1, 7, u'£'+title_export.avg_comp_price, style_more)
            else:
                sheet1.write(1, 7, u'£'+title_export.avg_comp_price, style_less)
    else:
        sheet1.write(1, 7, u'£'+title_export.avg_comp_price, style_less)
        
    for i in range(8):
        sheet1.col(i).width = 6000
    
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename= Product '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    book.save(response)
    return response
    

def detail(request):
    
    url1 = request.GET['1'] #ncchomelearning.co.uk
    url2 = request.GET['2'] #mydistance-learning-college
    url3 = request.GET['3'] #distance-learning-centre
    url4 = request.GET['4'] #openstudycollege
    url5 = request.GET['5'] #ukopencollege
    url6 = request.GET['6'].replace('/#/', '/') #edistancelearning
    title = request.GET['7']
    
    prices = []
    count = 0
    total_price = 0
    average_price = 0
    title = title.strip()
    prices.append(('Title', title))
    try:
        title_query = data.objects.get(title = title)
        if title.lower() == title_query.title.lower():
            if url1!= '':
                op = urllib2.urlopen(url1)
                src = op.read()
                parsed_src = html.fromstring(src)
                price = parsed_src.xpath("//span[@class='price']/text()")
                if price:
                    ncc_price = price[0].replace('Now:','').strip().replace(u'\xa3','')
                    prices.append(('ncchomelearning.co.uk', ncc_price))
                    title_query.ncchomelearning_url = url1
                    title_query.ncchomelearning_price = ncc_price
                else:
                    title_query.ncchomelearning_url = url1
                    title_query.ncchomelearning_price = ''
                    prices.append(('ncchomelearning.co.uk', ''))
            else:
                title_query.ncchomelearning_url = ''
                title_query.ncchomelearning_price = ''
                
            if url2!= '':
                op = urllib2.urlopen(url2)
                src = op.read()
                parsed_src = html.fromstring(src)
                deal_price = parsed_src.xpath("//div[@class='ourpricevalue']/span/text()")
                if deal_price:
                    price = deal_price
                else:
                    price = parsed_src.xpath("//span[@class='price']/text()")
                if price:
                    count = count+1
                    mydis_price = price[0].replace(u'\xa3','').strip()
                    prices.append(('mydistance-learning-college.com', mydis_price))
                    total_price = total_price + float(mydis_price)
                    title_query.mydistance_learning_college_url = url2
                    title_query.mydistance_learning_college_price = mydis_price
                else:
                    title_query.mydistance_learning_college_url = url2
                    title_query.mydistance_learning_college_price = ''
                    prices.append(('mydistance-learning-college.com', ''))
            else:
                title_query.mydistance_learning_college_url = ''
                title_query.mydistance_learning_college_price = ''
            
            if url3!= '': 
                op = urllib2.urlopen(url3)
                src = op.read()
                parsed_src = html.fromstring(src)
                price = parsed_src.xpath("//span[@class='price']/text()")
                if price:
                    count = count+1
                    dis_learn_centre_price = price[0].replace(u'\xa3','')
                    prices.append(('distance-learning-centre.co.uk', dis_learn_centre_price))
                    total_price = total_price + float(dis_learn_centre_price)
                    title_query.distance_learning_centre_url = url3
                    title_query.distance_learning_centre_price = dis_learn_centre_price
                else:
                    title_query.distance_learning_centre_url = url3
                    title_query.distance_learning_centre_price = ''
                    prices.append(('distance-learning-centre.co.uk', ''))
            else:
                title_query.distance_learning_centre_url = ''
                title_query.distance_learning_centre_price = ''
            
            if url4!= '':
                op = urllib2.urlopen(url4)
                src = op.read()
                parsed_src = html.fromstring(src)
                price = parsed_src.xpath("//span[@id='fullpaymentprice']/text()")
    #                price = re.findall('<span id="fullpaymentprice">(.*?)</', src)
                if price:
                    count = count+1
                    openstudycollege_price = price[0].replace(u'\xa3','')
                    prices.append(('openstudycollege.com', openstudycollege_price))
                    total_price = total_price + float(openstudycollege_price)
                    title_query.openstudycollege_url = url4
                    title_query.openstudycollege_price = openstudycollege_price
                else:
                    title_query.openstudycollege_url = url4
                    title_query.openstudycollege_price = ''
                    prices.append(('openstudycollege.com', ''))
            else:
                title_query.openstudycollege_url = ''
                title_query.openstudycollege_price = ''
            
            if url5!= '':
                op = urllib2.urlopen(url5)
                src = op.read()
                parsed_src = html.fromstring(src)
                price = parsed_src.xpath("//option[contains(text(),'Pay in Full')]/text()")
    #                price = re.findall('Pay in Full (.*?)</', src)
                if price:
                    count = count+1
                    ukopencollege_price = price[0].rsplit(' ',1)[-1].replace(u'\xa3','')
                    prices.append(('ukopencollege.co.uk', ukopencollege_price))
                    total_price = total_price + float(ukopencollege_price)
                    title_query.ukopencollege_url = url5
                    title_query.ukopencollege_price = ukopencollege_price
                else:
                    title_query.ukopencollege_url = url5
                    title_query.ukopencollege_price = ''
                    prices.append(('ukopencollege.co.uk', ''))
            else:
                title_query.ukopencollege_url = ''
                title_query.ukopencollege_price = ''
            
            if url6!= '':
                op = urllib2.urlopen(url6)
                src = op.read()
                parsed_src = html.fromstring(src)
                price = parsed_src.xpath("//td[contains(text(),'Enrolment Fee')]/following-sibling::td[1]/text()")
                if price:
                    count = count+1
                    edistancelearning_price = price[0].replace(u'\xa3','')
                    edistancelearning_price_discounted = (float(edistancelearning_price)*20)/100
                    edistancelearning_price_actual = float(edistancelearning_price)-float(edistancelearning_price_discounted)
                    prices.append(('edistancelearning.co.uk', edistancelearning_price_actual))
                    total_price = total_price + float(edistancelearning_price_actual)
                    title_query.edistancelearning_url = url6
                    title_query.edistancelearning_price = edistancelearning_price_actual
                else:
                    title_query.edistancelearning_url = url6
                    title_query.edistancelearning_price = ''
                    prices.append(('edistancelearning.co.uk', ''))
            else:
                title_query.edistancelearning_url = ''
                title_query.edistancelearning_price = ''
            if count != 0:
                average_price = "%.2f"%(float(total_price)/count)
                prices.append(('Average Price', average_price))
                title_query.avg_comp_price = average_price
            else:
                average_price = "0.00"
                prices.append(('Average Price', average_price))
                title_query.avg_comp_price = average_price
                
            obj = title_query.save()
    except:
#        raise
        data_obj = data()
        data_obj.title = title
        if url1!= '':
            op = urllib2.urlopen(url1)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                ncc_price = price[0].replace('Now:','').strip().replace(u'\xa3','')
                prices.append(('ncchomelearning.co.uk', ncc_price))
                data_obj.ncchomelearning_url = url1
                data_obj.ncchomelearning_price = ncc_price
            else:
                data_obj.ncchomelearning_url = url1
                data_obj.ncchomelearning_price = ''
                prices.append(('ncchomelearning.co.uk', ''))
        else:
            data_obj.ncchomelearning_url = ''
            data_obj.ncchomelearning_price = ''
            
        if url2!= '':
            op = urllib2.urlopen(url2)
            src = op.read()
            parsed_src = html.fromstring(src)
            deal_price = parsed_src.xpath("//div[@class='ourpricevalue']/span/text()")
            if deal_price:
                price = deal_price
            else:
                price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                count = count+1
                mydis_price = price[0].replace(u'\xa3','').strip()
                prices.append(('mydistance-learning-college.com', mydis_price))
                total_price = total_price + float(mydis_price)
                data_obj.mydistance_learning_college_url = url2
                data_obj.mydistance_learning_college_price = mydis_price
            else:
                data_obj.mydistance_learning_college_url = url2
                data_obj.mydistance_learning_college_price = ''
                prices.append(('mydistance-learning-college.com', ''))
        else:
            data_obj.mydistance_learning_college_url = ''
            data_obj.mydistance_learning_college_price = ''
        
        if url3!= '': 
            op = urllib2.urlopen(url3)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//span[@class='price']/text()")
            if price:
                count = count+1
                dis_learn_centre_price = price[0].replace(u'\xa3','')
                prices.append(('distance-learning-centre.co.uk', dis_learn_centre_price))
                total_price = total_price + float(dis_learn_centre_price)
                data_obj.distance_learning_centre_url = url3
                data_obj.distance_learning_centre_price = dis_learn_centre_price
            else:
                data_obj.distance_learning_centre_url = url3
                data_obj.distance_learning_centre_price = ''
                prices.append(('distance-learning-centre.co.uk', ''))
        else:
            data_obj.distance_learning_centre_url = ''
            data_obj.distance_learning_centre_price = ''
        
        if url4!= '':
            op = urllib2.urlopen(url4)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//span[@id='fullpaymentprice']/text()")
#                price = re.findall('<span id="fullpaymentprice">(.*?)</', src)
            if price:
                count = count+1
                openstudycollege_price = price[0].replace(u'\xa3','')
                prices.append(('openstudycollege.com', openstudycollege_price))
                total_price = total_price + float(openstudycollege_price)
                data_obj.openstudycollege_url = url4
                data_obj.openstudycollege_price = openstudycollege_price
            else:
                data_obj.openstudycollege_url = url4
                data_obj.openstudycollege_price = ''
                prices.append(('openstudycollege.com', ''))
        else:
            data_obj.openstudycollege_url = ''
            data_obj.openstudycollege_price = ''
        
        if url5!= '':
            op = urllib2.urlopen(url5)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//option[contains(text(),'Pay in Full')]/text()")
#                price = re.findall('Pay in Full (.*?)</', src)
            if price:
                count = count+1
                ukopencollege_price = price[0].rsplit(' ',1)[-1].replace(u'\xa3','')
                prices.append(('ukopencollege.co.uk', ukopencollege_price))
                total_price = total_price + float(ukopencollege_price)
                data_obj.ukopencollege_url = url5
                data_obj.ukopencollege_price = ukopencollege_price
            else:
                data_obj.ukopencollege_url = url5
                data_obj.ukopencollege_price = ''
                prices.append(('ukopencollege.co.uk', ''))
        else:
            data_obj.ukopencollege_url = ''
            data_obj.ukopencollege_price = ''
        
        if url6!= '':
            op = urllib2.urlopen(url6)
            src = op.read()
            parsed_src = html.fromstring(src)
            price = parsed_src.xpath("//td[contains(text(),'Enrolment Fee')]/following-sibling::td[1]/text()")
            if price:
                count = count+1
                edistancelearning_price = price[0].replace(u'\xa3','')
                edistancelearning_price_discounted = (float(edistancelearning_price)*20)/100
                edistancelearning_price_actual = float(edistancelearning_price)-float(edistancelearning_price_discounted)
                prices.append(('edistancelearning.co.uk', edistancelearning_price_actual))
                total_price = total_price + float(edistancelearning_price_actual)
                data_obj.edistancelearning_url = url6
                data_obj.edistancelearning_price = edistancelearning_price_actual
            else:
                data_obj.edistancelearning_url = url6
                data_obj.edistancelearning_price = ''
                prices.append(('edistancelearning.co.uk', ''))
        else:
            data_obj.edistancelearning_url = ''
            data_obj.edistancelearning_price = ''

        if count != 0:
            average_price = float(float(total_price)/count)
            prices.append(('Average Price', average_price))
            data_obj.avg_comp_price = average_price
        else:
            average_price = 0
            prices.append(('Average Price', average_price))
            data_obj.avg_comp_price = average_price
            
        obj = data_obj.save()
        
    context = {'results': prices}
    
    return render_to_response('pricing/index.html', context,
                                                    context_instance=RequestContext(request))# Create your views here.
    
def list(request):
    context = {'query_data': data.objects.all()}

    return render_to_response('pricing/index.html', context,
                              context_instance=RequestContext(request))

def exportlist(request):
    
    data_export = data.objects.all()
    
    book = Workbook(encoding='utf-8')
    sheet1 = book.add_sheet('Sheet 1', cell_overwrite_ok=True)
    book.add_sheet('Sheet 2')
    
    header = ['Title','ncchomelearning.co.uk','mydistance-learning-college.com',
              'distance-learning-centre.co.uk','openstudycollege.com',
              'ukopencollege.co.uk','edistancelearning.co.uk', 'Competitor Avg. price']
    for i in range(8):
        sheet1.write(0, i, header[i], xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;'))
    
    count = 1
    for title_export in data_export:
        sheet1.write(count, 0, title_export.title)
        
        if title_export.ncchomelearning_price.strip() !="":
            sheet1.write(count, 1, u'£'+title_export.ncchomelearning_price)
        else:
            sheet1.write(count, 1, '')
            
        style_less = xlwt.easyxf('pattern: pattern solid, fore_colour rose;'
                                 'alignment: horiz center;'
                                  'borders: left thin, right thin, top thin, bottom thin;')
        style_more = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;'
                                 'alignment: horiz center;'
                                 'borders: left thin, right thin, top thin, bottom thin;')
        if title_export.ncchomelearning_price.strip() != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.mydistance_learning_college_price.strip() != "": 
                if float(title_export.ncchomelearning_price) <= float(title_export.mydistance_learning_college_price):
                    sheet1.write(count, 2, u'£'+title_export.mydistance_learning_college_price, style_more)
                else:
                    sheet1.write(count, 2, u'£'+title_export.mydistance_learning_college_price, style_less)
        else:
            sheet1.write(count, 2, u'£'+title_export.mydistance_learning_college_price, style_less)
            
        if title_export.ncchomelearning_price.strip() != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.distance_learning_centre_price.strip() != "":
                if float(title_export.ncchomelearning_price) <= float(title_export.distance_learning_centre_price):
                    sheet1.write(count, 3, u'£'+title_export.distance_learning_centre_price, style_more)
                else:
                    sheet1.write(count, 3, u'£'+title_export.distance_learning_centre_price, style_less)
        else:
            sheet1.write(count, 3, u'£'+title_export.distance_learning_centre_price, style_less)
        
        if title_export.ncchomelearning_price.strip() != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.openstudycollege_price.strip() != "":
                if float(title_export.ncchomelearning_price) <= float(title_export.openstudycollege_price):
                    sheet1.write(count, 4, u'£'+title_export.openstudycollege_price, style_more)
                else:
                    sheet1.write(count, 4, u'£'+title_export.openstudycollege_price, style_less)
        else:
            sheet1.write(count, 4, u'£'+title_export.openstudycollege_price, style_less)
            
        if title_export.ncchomelearning_price.strip() != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.ukopencollege_price.strip() != "":
                if float(title_export.ncchomelearning_price) <= float(title_export.ukopencollege_price):
                    sheet1.write(count, 5, u'£'+title_export.ukopencollege_price, style_more)
                else:
                    sheet1.write(count, 5, u'£'+title_export.ukopencollege_price, style_less)
        else:
            sheet1.write(count, 5, u'£'+title_export.ukopencollege_price, style_less)
        
        if title_export.ncchomelearning_price.strip() != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.edistancelearning_price.strip() != "":
                if float(title_export.ncchomelearning_price) <= float(title_export.edistancelearning_price):
                    sheet1.write(count, 6, u'£'+title_export.edistancelearning_price, style_more)
                else:
                    sheet1.write(count, 6, u'£'+title_export.edistancelearning_price, style_less)
        else:
            sheet1.write(count, 6, u'£'+title_export.edistancelearning_price, style_less)
    
        if title_export.ncchomelearning_price.strip() != '' and title_export.avg_comp_price != '':
            if title_export.ncchomelearning_price.strip() !="" and title_export.mydistance_learning_college_price.strip() != "":
                if float(title_export.ncchomelearning_price) <= float(title_export.avg_comp_price):
                    sheet1.write(count, 7, u'£'+title_export.avg_comp_price, style_more)
                else:
                    sheet1.write(count, 7, u'£'+title_export.avg_comp_price, style_less)
        else:
            sheet1.write(count, 7, '', style_less)

	count = count+1
        
    for i in range(8):
        sheet1.col(i).width = 6000
    
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename= Products list '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    book.save(response)
    return response
