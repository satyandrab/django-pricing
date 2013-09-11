# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from lxml import html
import re
import urllib2
from django.http import Http404
from models import data
from django.core.context_processors import csrf


def index(request):
#     latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
#     template = loader.get_template('polls/index.html')
#     context = RequestContext(request, {
#         'latest_poll_list': latest_poll_list,
#     })
#     return HttpResponse(template.render(context))

#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
    context = {'results': None}

    return render_to_response('pricing/index.html', context)


def detail(request):
#     try:
#         poll = Poll.objects.get(pk=poll_id)
#     except Poll.DoesNotExist:
#         raise Http404
#     return render(request, 'polls/detail.html', {'poll': poll})
    
    url1 = request.GET['1']
    url2 = request.GET['2']
    url3 = request.GET['3']
    url4 = request.GET['4']
    url5 = request.GET['5']
    url6 = request.GET['6']
    title = request.GET['7']
    
    prices = []
    count = 0
    total_price = 0
    average_price = 0
    title = title.strip()
    prices.append(('Title', title))
    title_query = data.objects.get(title = title)
    if title.lower() == title_query.title.lower():
        for u in [url1, url2, url3, url4, url5, url6]:
            try:
                op = urllib2.urlopen(u)
                src = op.read()
                if 'ncchomelearning.co.uk' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span id="sp_price" class="total-value">(.*?)</', src)
                    if price:
    #                    count = count+1
                        ncc_price = price[0].replace('Now:','').strip().replace(u'\xa3','')
                        prices.append(('ncchomelearning.co.uk', ncc_price))
    #                    total_price = float(ncc_price)
                        title_query.ncchomelearning_url = u
                        title_query.ncchomelearning_price = ncc_price
                    else:
                        prices.append(u)
                if 'mydistance-learning' in u:
                    parsed_src = html.fromstring(src)
                    deal_price = parsed_src.xpath("//div[@class='ourpricevalue']/span/text()")
                    print deal_price
                    if deal_price:
                        price = deal_price
                    else:
                        price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span id="sp_price" class="total-value">(.*?)</', src)
                    if price:
                        count = count+1
                        mydis_price = price[0].replace(u'\xa3','').strip()
                        prices.append(('mydistance-learning-college.com', mydis_price))
                        total_price = total_price + float(mydis_price)
                        title_query.mydistance_learning_college_url = u
                        title_query.mydistance_learning_college_price = mydis_price
                    else:
                        prices.append(u)
                elif 'distance-learning-centre.' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span class="price">(.*?)</', src)
                    if price:
                        count = count+1
                        dis_learn_centre_price = price[0].replace(u'\xa3','')
                        prices.append(('distance-learning-centre.co.uk', dis_learn_centre_price))
                        total_price = total_price + float(dis_learn_centre_price)
                        title_query.distance_learning_centre_url = u
                        title_query.distance_learning_centre_price = dis_learn_centre_price
                    else:
                        prices.append(u)
                elif 'openstudycollege' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@id='fullpaymentprice']/text()")
    #                price = re.findall('<span id="fullpaymentprice">(.*?)</', src)
                    if price:
                        count = count+1
                        openstudycollege_price = price[0].replace(u'\xa3','')
                        prices.append(('openstudycollege.com', openstudycollege_price))
                        total_price = total_price + float(openstudycollege_price)
                        title_query.openstudycollege_url = u
                        title_query.openstudycollege_price = openstudycollege_price
                    else:
                        prices.append(u)
                elif 'ukopencollege' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//option[contains(text(),'Pay in Full')]/text()")
    #                price = re.findall('Pay in Full (.*?)</', src)
                    if price:
                        count = count+1
                        ukopencollege_price = price[0].rsplit(' ',1)[-1].replace(u'\xa3','')
                        prices.append(('ukopencollege.co.uk', ukopencollege_price))
                        total_price = total_price + float(ukopencollege_price)
                        title_query.ukopencollege_url = u
                        title_query.ukopencollege_price = ukopencollege_price
                    else:
                        prices.append(u)
                elif 'edistancelearning' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//td[contains(text(),'Enrolment Fee')]/following-sibling::td[1]/text()")
    #                price = re.findall('<td class="bodytext">(.*?)</', src)
                    if price:
                        count = count+1
                        edistancelearning_price = price[0].replace(u'\xa3','')
                        prices.append(('edistancelearning.co.uk', edistancelearning_price))
                        total_price = total_price + float(edistancelearning_price)
                        title_query.edistancelearning_url = u
                        title_query.edistancelearning_price = edistancelearning_price
                    else:
                        prices.append(u)
            
            except ValueError, e:
                prices.append("Not a valid URL")
        average_price = float(float(total_price)/count)
        prices.append(('Average Price', average_price))
        title_query.avg_comp_price = average_price
        obj = title_query.save()
        print obj
    else:
        data_obj = data()
        data_obj.title = title
        for u in [url1, url2, url3, url4, url5, url6]:
            try:
                op = urllib2.urlopen(u)
                src = op.read()
                if 'ncchomelearning.co.uk' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span id="sp_price" class="total-value">(.*?)</', src)
                    if price:
    #                    count = count+1
                        ncc_price = price[0].replace('Now:','').strip().replace(u'\xa3','')
                        prices.append(('ncchomelearning.co.uk', ncc_price))
    #                    total_price = float(ncc_price)
                        data_obj.ncchomelearning_url = u
                        data_obj.ncchomelearning_price = ncc_price
                    else:
                        prices.append(u)
                if 'mydistance-learning' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span id="sp_price" class="total-value">(.*?)</', src)
                    if price:
                        count = count+1
                        mydis_price = price[0].replace(u'\xa3','').strip()
                        prices.append(('mydistance-learning-college.com', mydis_price))
                        total_price = total_price + float(mydis_price)
                        data_obj.mydistance_learning_college_url = u
                        data_obj.mydistance_learning_college_price = mydis_price
                    else:
                        prices.append(u)
                elif 'distance-learning-centre.' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@class='price']/text()")
    #                price = re.findall('<span class="price">(.*?)</', src)
                    if price:
                        count = count+1
                        dis_learn_centre_price = price[0].replace(u'\xa3','')
                        prices.append(('distance-learning-centre.co.uk', dis_learn_centre_price))
                        total_price = total_price + float(dis_learn_centre_price)
                        data_obj.distance_learning_centre_url = u
                        data_obj.distance_learning_centre_price = dis_learn_centre_price
                    else:
                        prices.append(u)
                elif 'openstudycollege' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//span[@id='fullpaymentprice']/text()")
    #                price = re.findall('<span id="fullpaymentprice">(.*?)</', src)
                    if price:
                        count = count+1
                        openstudycollege_price = price[0].replace(u'\xa3','')
                        prices.append(('openstudycollege.com', openstudycollege_price))
                        total_price = total_price + float(openstudycollege_price)
                        data_obj.openstudycollege_url = u
                        data_obj.openstudycollege_price = openstudycollege_price
                    else:
                        prices.append(u)
                elif 'ukopencollege' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//option[contains(text(),'Pay in Full')]/text()")
    #                price = re.findall('Pay in Full (.*?)</', src)
                    if price:
                        count = count+1
                        ukopencollege_price = price[0].rsplit(' ',1)[-1].replace(u'\xa3','')
                        prices.append(('ukopencollege.co.uk', ukopencollege_price))
                        total_price = total_price + float(ukopencollege_price)
                        data_obj.ukopencollege_url = u
                        data_obj.ukopencollege_price = ukopencollege_price
                    else:
                        prices.append(u)
                elif 'edistancelearning' in u:
                    parsed_src = html.fromstring(src)
                    price = parsed_src.xpath("//td[contains(text(),'Enrolment Fee')]/following-sibling::td[1]/text()")
    #                price = re.findall('<td class="bodytext">(.*?)</', src)
                    if price:
                        count = count+1
                        edistancelearning_price = price[0].replace(u'\xa3','')
                        prices.append(('edistancelearning.co.uk', edistancelearning_price))
                        total_price = total_price + float(edistancelearning_price)
                        data_obj.edistancelearning_url = u
                        data_obj.edistancelearning_price = edistancelearning_price
                    else:
                        prices.append(u)
            
            except ValueError, e:
                prices.append("Not a valid URL")
        average_price = float(float(total_price)/count)
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
