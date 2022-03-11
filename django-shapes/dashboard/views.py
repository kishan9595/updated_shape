from email import message
from django.shortcuts import render, redirect
from .form import *
from django.contrib import messages
import datetime
from django.views import View
from django.http import HttpResponse, JsonResponse, request, HttpResponseRedirect
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.utils.decorators import method_decorator
import re
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .helpers import *
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from reportlab.pdfgen import canvas
from weasyprint import HTML
from itertools import groupby
regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

regex2 = r'\b^[a-zA-Z ]*$\b'

phone_regex = r"^(\d{10}|\d{11}|\d{12})$"
# def check(email):
#     if(re.fullmatch(regex, email)):
#         pass

#     else:
#         messages.error(request, 'Email is invalid')
#         re


def login_user(request):
    if request.method == "POST":
        print(request.POST.values())
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "User login Successfully")
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"message": "Invalid Credentials"})

    return render(request, "login.html")


class ClientListing(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request):

        if request.GET.get('id') and request.GET.get('ajax_req'):
            resp = list(ClientTable.objects.filter(id=request.GET.get('id'),user=request.user).values('name','assessment'))
            return JsonResponse({'data': resp}, safe=False)

        if request.GET.get('id') and request.GET.get('client_modal'):
            print("Trig")
            asess_ls=[]
            ob = ClientTable.objects.get(id=request.GET.get('id'),user=request.user)
            asess_ls.append(str(ob.assessment))
            resp = list(ClientTable.objects.filter(id=request.GET.get('id'),user=request.user)
            .values('name','gender','assessment','dob','age','email','phone','alternate_phone','mother_tongue',
            'father_name','mother_name','address','branch','discontinious','discontinious_on','assessment',
            'slot_time_from','slot_time_to','theropy','chief_complaints','diagnosis','remarks'))
            resp[0]['asess_ls']=asess_ls
            
            return JsonResponse({'data': resp}, safe=False)
            

        
        date = request.GET.get("date", None)
        sort_by = request.GET.get("sort_by", None)
        search = request.GET.get("search", None)
        print(date, "date-view")
        print(request.GET, 'request.GET,request.GET')
        if request.GET.get("search") and request.GET.get("date"):
            print("me hu dono me")
            blnk_dic = {}
            clients = ClientTable.objects.filter(
                
                Q(name__icontains=request.GET.get("search"))
                | Q(phone__icontains=request.GET.get("search"))
                | Q(id__icontains=request.GET.get("search")),created_on=request.GET.get("date") ,user=request.user)
            print(clients, "clientss check both")
            for k in clients:
                blnk_dic[k.id] = k.assessment
            print(clients,'clients')
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)

            try:
                client = paginator.page(page)
                print("client", client)
            except PageNotAnInteger:
                client = paginator.page(1)
                print("client", client)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string("listing-filter.html", {"client": client,"blnk_dic":blnk_dic})
            return JsonResponse({"html": html})
        if request.GET.get("date") and not request.GET.get("search"):
            blnk_dic = {}
            print("in date")
            clients = ClientTable.objects.filter(created_on=request.GET.get("date") ,user=request.user)
            for k in clients:
                blnk_dic[k.id] = k.assessment
            print(clients,'clients')
            print(blnk_dic, 'blank')
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)

            try:
                client = paginator.page(page)
                print("client", client)
            except PageNotAnInteger:
                client = paginator.page(1)
                print("client", client)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string("listing-filter.html", {"client": client,"blnk_dic":blnk_dic})
            return JsonResponse({"html": html})
        if sort_by == "dsc":
            status = {}
            blnk_dic = {}
            
            clients = ClientTable.objects.filter(user=request.user).order_by("id")
            for k in clients:
                blnk_dic[k.id] = k.assessment

                try:
                    status_client = Assesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status

                except Assesment.DoesNotExist:
                    pass

                try:
                    status_client = STAssesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status
                except STAssesment.DoesNotExist:
                    pass

                try:
                    status_client = OTAssesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status
                except OTAssesment.DoesNotExist:
                    pass
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            print(client)
            html = render_to_string("listing-filter.html", {"client": client,"blnk_dic":blnk_dic})
            return JsonResponse({"html": html})
        if sort_by == "asc":
            blnk_dic = {}
            status = {}
            clients = ClientTable.objects.filter(user=request.user).order_by("-id")
            for k in clients:
                blnk_dic[k.id] = k.assessment

                try:
                    status_client = Assesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status

                except Assesment.DoesNotExist:
                    pass

                try:
                    status_client = STAssesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status
                except STAssesment.DoesNotExist:
                    pass

                try:
                    status_client = OTAssesment.objects.get(clienttable=k.id)
                    status[k.id] = status_client.Status
                except OTAssesment.DoesNotExist:
                    pass
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string(
                "listing-filter.html", {"client": client, "blnk_dic": blnk_dic}
            )
            return JsonResponse({"html": html})
        if request.GET.get("search") and not request.GET.get("date"):
            blnk_dic = {}
            print("I AM SEARCH", search)
            clients = ClientTable.objects.filter(
                
                Q(name__icontains=request.GET.get("search"))
                | Q(phone__icontains=request.GET.get("search"))
                | Q(id__icontains=request.GET.get("search")),user=request.user
            )
            for k in clients:
                blnk_dic[k.id] = k.assessment

            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string(
                "listing-filter.html", {"client": client, "blnk_dic": blnk_dic}
            )
            return JsonResponse({"html": html})

        elif search == "":
            blnk_dic = {}
            clients = ClientTable.objects.filter(user=request.user)
            for k in clients:
                blnk_dic[k.id] = k.assessment

            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string(
                "listing-filter.html", {"client": client, "blnk_dic": blnk_dic}
            )
            return JsonResponse({"html": html})

        else:
            blnk_dic = {}
            client_list = ClientTable.objects.filter(user=request.user)
            for k in client_list:
                blnk_dic[k.id] = k.assessment
            print(blnk_dic)
            page = request.GET.get("page", 1)

            paginator = Paginator(client_list, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            return render(
                request, "client-listing.html", {"client": client, "blnk_dic": blnk_dic}
            )


class Client(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        return render(request, "client.html")



    def post(self, request):
        if ClientTable.objects.filter(phone=request.POST.get("phone")).exists():
            print("exist5")
            return render(
                request, "client.html", {"phone_error": "Mobile number already exists"}
            )

        elif ClientTable.objects.filter(email=request.POST.get("email")).exists():
            print("exist5")
            return render(
                request, "client.html", {"email_error": "Email already exists"}
            )
        elif not re.fullmatch(regex, request.POST.get("email")):
            print("exist4")
            return render(request, "client.html", {"email_error": "Email is not valid"})

        elif not re.fullmatch(regex2, request.POST.get("name")):
            print("exist6")
            return render(
                request,
                "client.html",
                {"name_error": "Only Characters are required"},
            )
        elif not re.fullmatch(regex2, request.POST.get("mother_tongue")):
            print("exist3")
            return render(request, 'client.html',{'mother_tongue_error':'Only Characters are required'})

        elif not re.fullmatch(phone_regex, request.POST.get("phone")):
            print("exist")
            return render(
                request, "client.html", {"phone_error": "Phone number is not valid"}
            )

        elif not re.fullmatch(phone_regex, request.POST.get("alternate_phone")):
            print("exist1")
            return render(
                request,
                "client.html",
                {"alternate_error": "Alternate Phone number is not valid"},
            )

        else:
            if request.POST.get('send_mail') == 'on':
                template_data = {'client_name': request.POST.get("name"), 'client_address': request.POST.get("address"),
                                'assignment_name': request.POST.getlist("assessment"),
                                
                                }
                send_email(request.POST.get("email"),template_data)
            user=request.user
            name = request.POST.get("name")
            gender = request.POST.get("gender")
            dob = request.POST.get("dob")
            age = request.POST.get("age")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            alternate_phone = request.POST.get("alternate_phone")
            mother_tongue = request.POST.get("mother_tongue")
            father_name = request.POST.get("father_name")
            mother_name = request.POST.get("mother_name")
            address = request.POST.get("address")
            branch = request.POST.get("branch")
            discontinious = request.POST.get("discontinious", False)
            discontinious_on = request.POST.get("discontinious_on")
            assessment = request.POST.getlist("assessment")
            
            slot_time_from = request.POST.get("slot_time_from")
            slot_time_to = request.POST.get("slot_time_to")
            theropy = request.POST.getlist("theropy")
            print(theropy, 'theropy check 2')
            chief_complaints = request.POST.get("chief_complaints")
            diagnosis = request.POST.get("diagnosis")
            remarks = request.POST.get("remarks")
            created_on = datetime.datetime.now()
            client = ClientTable.objects.create(
                user=request.user,
                name=re.sub(" +", " ", name),
                age=age,
                phone=phone,
                dob=dob,
                gender=gender,
                email=re.sub(" +", " ", email),
                alternate_phone=alternate_phone,
                mother_tongue=re.sub(" +", " ", mother_tongue),
                father_name=re.sub(" +", " ", father_name),
                mother_name=re.sub(" +", " ", mother_name),
                address=re.sub(" +", " ", address),
                branch=re.sub(" +", " ", branch),
                discontinious=discontinious,
                discontinious_on=discontinious_on,
                assessment=assessment,
                slot_time_from=slot_time_from,
                slot_time_to=slot_time_to,
                theropy=theropy,
                chief_complaints=re.sub(" +", " ", chief_complaints),
                diagnosis=re.sub(" +", " ", diagnosis),
                remarks=re.sub(" +", " ", remarks),
                created_on=created_on,
                created_by=request.user.username,
            )
            print(type(theropy))
            messages.success(request, "Form created successful")
            return redirect("dashboard")


# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    if request.method == "GET":
        labels = []
        data = []
        queryset = ClientTable.objects.filter(user=request.user).order_by("-assessment")
        for city in queryset:
            labels.append(city.assessment)
            data.append(city.assessment)
        passed = labels
        print(passed, 'passed')
        res = []

        for x in passed:
            if type(list(x)) == list:
                for b in x:
                    res.append(b)
            else:
                res.append(x)
        print('res',res)
       
        results = {value: len(list(freq)) for value, freq in groupby(sorted(res))}
        print(results, 'results')
        res_key = list(results.keys())
        res_val = list(results.values())
        print(res_key, "res_keyy")
        print(res_val, "res_val")
        
        #res_key = [ele for ele in reversed(res_key)]
        # res_val = [ele for ele in reversed(res_val)]
        print(res_key, res_val)
        return render(
            request, "listing-dashboard.html", {"labels": ['BT', 'OT', 'ST'], "data": res_val}
        )


class update(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        select_theropy = []
        assesment_client = []
        
        client = ClientTable.objects.get(id=id,user=request.user)
        
        for k in client.theropy:
            select_theropy.append(k)

        assesment_client.append(str(client.assessment))
        print(select_theropy, 'select_theropy')
        return render(request, "edit-client.html", {"client": client,"assesment_client":assesment_client,"theropy":client.theropy,"select_theropy":select_theropy})

    def post(self, request, id):
        print("postttt", request.POST.getlist("assessment"))
        client = ClientTable.objects.get(id=id,user=request.user)
        print(client.assessment,type(client.assessment))

        if not re.fullmatch(regex, request.POST.get("email")):
            print("SHOW")
            return render(request, 'edit-client.html',{'email_error':'Email is not valid','update_asses':request.POST.getlist("assessment"),'update_theropy':request.POST.getlist("theropy")})
        elif not re.fullmatch(regex2, request.POST.get('name').strip()):
            return render(request, 'edit-client.html',{'name_error':'Only Characters are required','update_asses':request.POST.getlist("assessment"),'update_theropy':request.POST.getlist("theropy")})
        elif not re.fullmatch(regex2, request.POST.get('mother_tongue').strip()):
            return render(request, 'edit-client.html',{'mother_tongue':'Only Characters are required','update_asses':request.POST.getlist("assessment"),'update_theropy':request.POST.getlist("theropy")})
        elif client.phone != request.POST.get("phone"):
            val = re.fullmatch(phone_regex, request.POST.get("phone"))
            if val is None:
                return render(
                    request, "edit-client.html", {"phone_error": "Phone number is not valid",'update_asses':request.POST.getlist("assessment"),'update_theropy':request.POST.getlist("theropy")}
                )
        elif client.alternate_phone != request.POST.get("alternate_phone"):
            val = re.fullmatch(phone_regex, request.POST.get("alternate_phone"))
            if val is None:
                return render(
                    request,
                    "edit-client.html",
                    {"alternate_phone": "Alternate Phone number is not valid",'update_asses':request.POST.getlist("assessment"),'update_theropy':request.POST.getlist("theropy")},
                )
        client.name = re.sub(" +", " ", request.POST.get("name"))
        client.age = request.POST.get("age")
        client.gender = request.POST.get("gender")
        client.dob = request.POST.get("dob")
        client.email = re.sub(" +", " ", request.POST.get("email"))
        client.phone = request.POST.get("phone")
        client.alternate_phone = request.POST.get("alternate_phone")
        client.mother_tongue = re.sub(" +", " ", request.POST.get("mother_tongue"))
        client.father_name = re.sub(" +", " ", request.POST.get("father_name"))
        client.mother_name = re.sub(" +", " ", request.POST.get("mother_name"))
        client.address = re.sub(" +", " ", request.POST.get("address"))
        client.branch = re.sub(" +", " ", request.POST.get("branch"))
        client.discontinious = request.POST.get("discontinious", False)
        client.discontinious_on = request.POST.get("discontinious_on")
        client.assessment = request.POST.getlist("assessment")
        client.slot_time_from = request.POST.get("slot_time_from")
        client.slot_time_to = request.POST.get("slot_time_to")
        client.theropy = request.POST.getlist("theropy")
        client.chief_complaints = re.sub(
            " +", " ", request.POST.get("chief_complaints")
        )
        client.diagnosis = re.sub(" +", " ", request.POST.get("diagnosis"))
        client.remarks = re.sub(" +", " ", request.POST.get("remarks"))
        client.modified_on = datetime.datetime.now()
        client.modified_by = request.user.username
        client.save()
        return redirect("client_listing")


# def update(request, id):
#     client = ClientTable.objects.get(id = id)
#     return render(request, 'edit-client.html', {'client':client})


class UserListing(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        sort_by = request.GET.get("sort_by")
        search = request.GET.get("search")
        if sort_by == "dsc":
            print("dsc")
            clients = User.objects.filter(created_by=request.user).order_by("id")
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            print(clients)
            html = render_to_string("listing-user-filter.html", {"client": client})
            return JsonResponse({"html": html})
        if sort_by == "asc":
            print("asc")
            clients = User.objects.filter(created_by=request.user).order_by("-id")
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string("listing-user-filter.html", {"client": client})
            return JsonResponse({"html": html})
        if search:
            print(request.GET.get("search"))
            clients = User.objects.filter(
                Q(username__icontains=request.GET.get("search"))
                | Q(department__icontains=request.GET.get("search")),created_by=request.user
            )
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string("listing-user-filter.html", {"client": client})
            return JsonResponse({"html": html})

        elif search == "":
            clients = User.objects.filter(created_by=request.user)
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string("listing-user-filter.html", {"client": client})
            return JsonResponse({"html": html})

        else:
            user_list = User.objects.filter(created_by=request.user)
            page = request.GET.get("page", 1)

            paginator = Paginator(user_list, 10)
            try:
                user = paginator.page(page)
            except PageNotAnInteger:
                user = paginator.page(1)
            except EmptyPage:
                user = paginator.page(paginator.num_pages)
            return render(request, "userlisting.html", {"user": user})


class CreateUser(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        return render(request, "user.html")

    def post(self, request):
        username = request.POST.get("username")
        department = request.POST.get("department")
        password = make_password(request.POST.get("password"))
        created_by= request.user
        User.objects.create(username=username, department=department, password=password, created_by=created_by)
        messages.success(request, "Form created successful")
        return redirect("user_listing")


class UpdateUser(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        client = User.objects.get(id=id)
        return render(request, "update_user.html", {"client": client})

    def post(self, request, id):
        username = request.POST.get("username")
        department = request.POST.get("department")
        password = make_password(request.POST.get("password"))

        User.objects.filter(id=id).update(
            username=username, department=department, password=password
        )
        return redirect("user_listing")


class assesment(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        if Assesment.objects.filter(clienttable_id=id).exists():
            messages.error(request, "Already Created")
            return redirect("client_listing")
        client = ClientTable.objects.get(id=id,user=request.user)
        return render(request, "assesment.html", {"client": client})

    def post(self, request, id):

        if request.POST.get('email_sent') == "on":
            template_data = {'client_name': request.POST.get("name"), 'client_address': request.POST.get("address"),
                                'assignment_name': ['BT'],
                                
                                }
            send_email(request.POST.get("email"),template_data)

        date_of_assessment = request.POST.get("date_of_assessment")
        prenatal_history = request.POST.get("prenatal_history")
        family_history = request.POST.get("family_history")
        development_history = request.POST.get("development_history")
        school_history = request.POST.get("school_history")
        tests_administered = request.POST.get("tests_administered")
        test_results = request.POST.get("test_results")
        behavioural_observation = request.POST.get("behavioural_observation")
        impression = request.POST.get("impression")
        recommendations = request.POST.get("recommendations")
        email_sent = request.POST.get("email_sent","")
        if request.POST.get("draft"):
            Status = "Draft"
        else:
            Status = "Submited"
        print(Status)
        if request.POST.get("Submited"):
            version = "Submited"
        else:
            version = ""
        client = Assesment.objects.create(
            date_of_assessment=date_of_assessment,
            prenatal_history=re.sub(" +", " ", prenatal_history),
            tests_administered=re.sub(" +", " ", tests_administered),
            test_results=test_results,
            behavioural_observation=re.sub(" +", " ", behavioural_observation),
            family_history=re.sub(" +", " ", family_history),
            development_history=re.sub(" +", " ", development_history),
            school_history=re.sub(" +", " ", school_history),
            recommendations=re.sub(" +", " ", recommendations),
            email_sent=email_sent,
            Status=Status,
            impression=re.sub(" +", " ", impression),
            version=version,
            created_by=request.user.username,
            therapist=request.user.username,
            clienttable_id=id,
        )
        messages.success(request, "Form created successful")
        return redirect("assesment_listing")


class STassesmentTable(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        if STAssesment.objects.filter(clienttable_id=id).exists():
            messages.error(request, "Already Created")
            return redirect("client_listing")
        client = ClientTable.objects.get(id=id,user=request.user)
        return render(request, "STAssesment.html", {"client": client})

    def post(self, request, id):
        date_of_assessment = request.POST.get("date_of_assessment")
        babbling = request.POST.get("babbling")
        first_word = request.POST.get("first_word")
        main_mode_comm = request.POST.get("main_mode_comm")
        family_history = request.POST.get("family_history")
        motor_developments = request.POST.get("motor_developments")
        oro_peripheral_mechanism = request.POST.get("oro_peripheral_mechanism")
        vegetative_skills = request.POST.get("vegetative_skills")
        vision = request.POST.get("vision")
        hearing = request.POST.get("hearing")
        response_to_name_call = request.POST.get("response_to_name_call")
        environmental_sounds = request.POST.get("environmental_sounds")
        eye_contact = request.POST.get("eye_contact")
        attention_to_sound = request.POST.get("attention_to_sound")
        imitation_to_body_movements = request.POST.get("imitation_to_body_movements")
        imitation_to_speech = request.POST.get("imitation_to_speech")
        attention_level = request.POST.get("attention_level")
        social_smile = request.POST.get("social_smile")
        initiates_interaction = request.POST.get("initiates_interaction")
        receptive_language = request.POST.get("receptive_language")
        expressive_language = request.POST.get("expressive_language")
        provisional_diagnosis = request.POST.get("provisional_diagnosis")
        recommendations = request.POST.get("recommendations")
        reels_RL_score = request.POST.get("reels_RL_score")
        reels_EL_score = request.POST.get("reels_EL_score")
        tests_administered = request.POST.get("tests_administered")
        if request.POST.get("draft"):
            Status = "Draft"
        else:
            Status = "Submited"
        client = STAssesment.objects.create(
            date_of_assessment=date_of_assessment,
            babbling=re.sub(" +", " ", babbling),
            first_word=re.sub(" +", " ", first_word),
            main_mode_comm=re.sub(" +", " ", main_mode_comm),
            family_history=re.sub(" +", " ", family_history),
            motor_developments=re.sub(" +", " ", motor_developments),
            oro_peripheral_mechanism=re.sub(" +", " ", oro_peripheral_mechanism),
            vegetative_skills=re.sub(" +", " ", vegetative_skills),
            vision=re.sub(" +", " ", vision),
            hearing=re.sub(" +", " ", hearing),
            response_to_name_call=re.sub(" +", " ", response_to_name_call),
            environmental_sounds=re.sub(" +", " ", environmental_sounds),
            eye_contact=re.sub(" +", " ", eye_contact),
            attention_to_sound=re.sub(" +", " ", attention_to_sound),
            imitation_to_body_movements=re.sub(" +", " ", imitation_to_body_movements),
            imitation_to_speech=re.sub(" +", " ", imitation_to_speech),
            attention_level=re.sub(" +", " ", attention_level),
            social_smile=re.sub(" +", " ", social_smile),
            initiates_interaction=re.sub(" +", " ", initiates_interaction),
            receptive_language=re.sub(" +", " ", receptive_language),
            expressive_language=re.sub(" +", " ", expressive_language),
            provisional_diagnosis=re.sub(" +", " ", provisional_diagnosis),
            recommendations=re.sub(" +", " ", recommendations),
            reels_RL_score=reels_RL_score,
            reels_EL_score=reels_EL_score,
            tests_administered=re.sub(" +", " ", tests_administered),
            therapist=request.user.username,
            clienttable_id=id,
            Status=Status,
        )
        messages.success(request, "Form created successful")
        return redirect("assesment_listing")


class OTAssesmentTable(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        if OTAssesment.objects.filter(clienttable_id=id).exists():
            messages.error(request, "Already Created")
            return redirect("client_listing")
        client = ClientTable.objects.get(id=id,user=request.user)
        return render(request, "OTAssessment.html", {"client": client})

    def post(self, request, id):
        date_of_assessment = request.POST.get("date_of_assessment")
        presenting_complaints = request.POST.get("presenting_complaints")
        milestone_development = request.POST.get("milestone_development")
        behavior_cognition = request.POST.get("behavior_cognition")
        cognitive_skills = request.POST.get("cognitive_skills")
        kinaesthesia = request.POST.get("kinaesthesia")
        if request.POST.get("draft"):
            Status = "Draft"
        else:
            Status = "Submited"
        client = OTAssesment.objects.create(
            date_of_assessment=date_of_assessment,
            presenting_complaints=re.sub(" +", " ", presenting_complaints),
            milestone_development=re.sub(" +", " ", milestone_development),
            behavior_cognition=re.sub(" +", " ", behavior_cognition),
            cognitive_skills=re.sub(" +", " ", cognitive_skills),
            kinaesthesia=re.sub(" +", " ", kinaesthesia),
            therapist=request.user.username,
            clienttable_id=id,
            Status=Status,
        )
        messages.success(request, "Form created successful")
        return redirect("assesment_listing")


class AssessmentListing(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request):

        if request.GET.get('obj') and request.GET.get('id') == "BT":
            resp = list(Assesment.objects.filter(clienttable=request.GET.get('obj')).values('Status'))
            if not resp:
                return JsonResponse({'data': "Not Started"}, safe=False)
            return JsonResponse({'data': resp}, safe=False)

        if request.GET.get('obj') and request.GET.get('id') == "ST":
            resp = list(STAssesment.objects.filter(clienttable=request.GET.get('obj')).values('Status'))
            if not resp:
                return JsonResponse({'data': "Not Started"}, safe=False)
            return JsonResponse({'data': resp}, safe=False)

        if request.GET.get('obj') and request.GET.get('id') == "OT":
            resp = list(OTAssesment.objects.filter(clienttable=request.GET.get('obj')).values('Status'))
            if not resp:
                return JsonResponse({'data': "Not Started"}, safe=False)
            return JsonResponse({'data': resp}, safe=False)

        sort_by = request.GET.get("sort_by")
        search = request.GET.get("search")
        print(search, "search")
        status = {}
        if sort_by == "dsc":
            status = {}
            blnk_dic = {}
            clients = ClientTable.objects.filter(user=request.user).order_by("id")
            for s in clients:
                blnk_dic[s.id]=s.assessment
            for a in clients:
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    print("CHK", status_client)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except STAssesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except OTAssesment.DoesNotExist as e:
                    status[a.id] = "None"
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            print(client)
            html = render_to_string(
                "listing-assessment-filter.html", {"client": client,'blnk_dic':blnk_dic,'status':status}
            )
            return JsonResponse({"html": html})
        if sort_by == "asc":
            status = {}
            blnk_dic = {}
            clients = ClientTable.objects.filter(user=request.user).order_by("-id")
            for s in clients:
                blnk_dic[s.id]=s.assessment
            for a in clients:
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    print("CHK", status_client)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except STAssesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except OTAssesment.DoesNotExist as e:
                    status[a.id] = "None"
            page = request.GET.get("page", 1)
            print("i am status ", status)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            print(status)
            html = render_to_string(
                "listing-assessment-filter.html", {"client": client,"status":status,"blnk_dic":blnk_dic}
            )
            return JsonResponse({"html": html})
        if search:
            blnk_dic={}

            clients = ClientTable.objects.filter(
                
                Q(assessment__icontains=request.GET.get("search"))
                | Q(name__icontains=request.GET.get("search"))
                | Q(id__icontains=request.GET.get("search")),user=request.user
            )
            # newly added
            for s in clients:
                blnk_dic[s.id] = s.assessment

            for a in clients:
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    print("CHK", status_client)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except STAssesment.DoesNotExist as e:
                    status[a.id] = "None"

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                    print("CHK", status_client)
                except OTAssesment.DoesNotExist as e:
                    status[a.id] = "None"

            # new
            username = request.user.username
            department = request.user.department

            client_ass = ClientTable.objects.filter(user=request.user)
            
            for a in client_ass:
                print(a.id)
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist:
                    pass

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except STAssesment.DoesNotExist:
                    pass

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except OTAssesment.DoesNotExist:
                    pass
            page = request.GET.get("page", 1)

            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)

            
            html = render_to_string(
                "listing-assessment-filter.html",
                {
                    "client": client,
                    "department": department,
                    "username": username,
                    "status": status,
                    "blnk_dic":blnk_dic
                },
            )
            return JsonResponse({"html": html})
        elif search == "":
            print("dscdfdsfhfhbhshfhbhb")
            status = {}
            blnk_dic={}
            clients = ClientTable.objects.filter(user=request.user)
            for a in clients:
                blnk_dic[a.id]=a.assessment
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist:
                    pass

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except STAssesment.DoesNotExist:
                    pass

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except OTAssesment.DoesNotExist:
                    pass
            username = request.user.username
            department = request.user.department

            page = request.GET.get("page", 1)
            paginator = Paginator(clients, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            html = render_to_string(
                "listing-assessment-filter.html",
                {
                    "client": client,
                    "status": status,
                    "department": department,
                    "username": username,
                    "blnk_dic": blnk_dic
                },
            )
            return JsonResponse({"html": html})
        else:
            blnk_dic ={}
            client_ass = ClientTable.objects.filter(user=request.user)
            for k in client_ass:
                blnk_dic[k.id]=k.assessment
            print(blnk_dic)
            print("client_assesment", client_ass)
            for a in client_ass:
                print(a.id, "check a ki id")
                try:
                    status_client = Assesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status

                except Assesment.DoesNotExist:
                    pass

                try:
                    status_client = STAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except STAssesment.DoesNotExist:
                    pass

                try:
                    status_client = OTAssesment.objects.get(clienttable=a.id)
                    status[a.id] = status_client.Status
                except OTAssesment.DoesNotExist:
                    pass

            page = request.GET.get("page", 1)
            print("i am status ", status)

            paginator = Paginator(client_ass, 10)
            try:
                client = paginator.page(page)
            except PageNotAnInteger:
                client = paginator.page(1)
            except EmptyPage:
                client = paginator.page(paginator.num_pages)
            username = request.user.username
            department = request.user.department
            return render(
                request,
                "assessment-listing.html",
                {
                    "client": client,
                    "username": username,
                    "department": department,
                    "status": status,
                    "blnk_dic":blnk_dic
                },
            )


class UpdateBtAssessment(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        try:
            client = Assesment.objects.filter(clienttable__id=id).get()
            return render(request, "edit-btassess.html", {"client": client})
        except:
            messages.error(request, f"Create BT Assesments first for id {id}")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def post(self, request, id):
        client = Assesment.objects.get(clienttable__id=id)
        client.date_of_assessment= request.POST.get('date_of_assessment')
        client.prenatal_history = re.sub(
            " +", " ", request.POST.get("prenatal_history")
        )
        client.family_history = re.sub(" +", " ", request.POST.get("family_history"))
        client.development_history = re.sub(
            " +", " ", request.POST.get("development_history")
        )
        client.school_history = re.sub(" +", " ", request.POST.get("school_history"))
        client.tests_administered = request.POST.get("tests_administered")
        client.test_results = request.POST.get("test_results")
        client.behavioural_observation = re.sub(
            " +", " ", request.POST.get("behavioural_observation")
        )
        client.impression = re.sub(" +", " ", request.POST.get("impression"))
        client.recommendations = re.sub(" +", " ", request.POST.get("recommendations"))
        client.email_sent = request.POST.get("email_sent","")
        if request.POST.get("draft"):
            client.Status = "Draft"
        else:
            client.Status = "Submited"
        client.version = "aaa"
        client.modified_on = datetime.datetime.now()
        client.modified_by = request.user.username
        client.save()
        return redirect("assesment_listing")


class UpdateStAssessment(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        try:
            client = STAssesment.objects.get(clienttable__id=id)
            return render(request, "edit-stassess.html", {"client": client})
        except:
            messages.error(request, f"Create ST Assesments first for id {id}")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def post(self, request, id):
        client = STAssesment.objects.get(clienttable__id=id)
        client.babbling = re.sub(" +", " ", request.POST.get("babbling"))
        client.first_word = re.sub(" +", " ", request.POST.get("first_word"))
        client.main_mode_comm = re.sub(" +", " ", request.POST.get("main_mode_comm"))
        client.family_history = re.sub(" +", " ", request.POST.get("family_history"))
        client.motor_developments = re.sub(
            " +", " ", request.POST.get("motor_developments")
        )
        client.oro_peripheral_mechanism = re.sub(
            " +", " ", request.POST.get("oro_peripheral_mechanism")
        )
        client.vegetative_skills = re.sub(
            " +", " ", request.POST.get("vegetative_skills")
        )
        client.vision = re.sub(" +", " ", request.POST.get("vision"))
        client.hearing = re.sub(" +", " ", request.POST.get("hearing"))
        client.response_to_name_call = re.sub(
            " +", " ", request.POST.get("response_to_name_call")
        )
        client.environmental_sounds = re.sub(
            " +", " ", request.POST.get("environmental_sounds")
        )
        client.eye_contact = re.sub(" +", " ", request.POST.get("eye_contact"))
        client.attention_to_sound = re.sub(
            " +", " ", request.POST.get("attention_to_sound")
        )
        client.imitation_to_body_movements = re.sub(
            " +", " ", request.POST.get("imitation_to_body_movements")
        )
        client.imitation_to_speech = re.sub(
            " +", " ", request.POST.get("imitation_to_speech")
        )
        client.attention_level = re.sub(" +", " ", request.POST.get("attention_level"))
        client.social_smile = re.sub(" +", " ", request.POST.get("social_smile"))
        client.initiates_interaction = re.sub(
            " +", " ", request.POST.get("initiates_interaction")
        )
        client.receptive_language = re.sub(
            " +", " ", request.POST.get("receptive_language")
        )
        client.expressive_language = re.sub(
            " +", " ", request.POST.get("expressive_language")
        )
        client.provisional_diagnosis = re.sub(
            " +", " ", request.POST.get("provisional_diagnosis")
        )
        client.recommendations = re.sub(" +", " ", request.POST.get("recommendations"))
        client.reels_RL_score = request.POST.get("reels_RL_score")
        client.reels_EL_score = request.POST.get("reels_EL_score")
        client.tests_administered = re.sub(
            " +", " ", request.POST.get("tests_administered")
        )
        client.modified_on = datetime.datetime.now()
        client.modified_by = request.user.username
        if request.POST.get("draft"):
            client.Status = "Draft"
        else:
            client.Status = "Submited"
        client.save()
        return redirect("assesment_listing")


class UpdateOtAssessment(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, id):
        try:
            client = OTAssesment.objects.filter(clienttable__id=id).get()
            return render(request, "edit-otassess.html", {"client": client})
        except:
            messages.error(request, f"Create OT Assesments first for id {id}")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    def post(self, request, id):
        client = OTAssesment.objects.filter(clienttable__id=id).get()
        client.date_of_assessment = request.POST.get("date_of_assessment")
        client.presenting_complaints = re.sub(
            " +", " ", request.POST.get("presenting_complaints")
        )
        client.milestone_development = re.sub(
            " +", " ", request.POST.get("milestone_development")
        )
        client.behavior_cognition = re.sub(
            " +", " ", request.POST.get("behavior_cognition")
        )
        client.cognitive_skills = re.sub(
            " +", " ", request.POST.get("cognitive_skills")
        )
        client.kinaesthesia = re.sub(" +", " ", request.POST.get("kinaesthesia"))
        client.modified_on = datetime.datetime.now()
        client.modified_by = request.user.username
        if request.POST.get("draft"):
            client.Status = "Draft"
        else:
            client.Status = "Submited"
        client.save()
        return redirect("assesment_listing")


def logout_user(request):
    logout(request)
    return redirect("login")

def download_pdf_file(request, id):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="mypdf.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    data = ClientTable.objects.filter(id=id)

    for k in data:

        if request.GET.get("assesment_id") == "BT":
            assesment_data = Assesment.objects.filter(clienttable=k.id)
            html_string = render_to_string("BT_pdf.html", {"data": assesment_data,"client_data":data})

            html = HTML(string=html_string)

            html.write_pdf(target="/tmp/mypdf.pdf")
            fs = FileSystemStorage("/tmp")

            with fs.open("mypdf.pdf") as pdf:
                response = HttpResponse(pdf, content_type="application/pdf")
                print("response1", response)
                response["Content-Disposition"] = 'attachment; filename="mypdf.pdf"'
            return response

        if request.GET.get("assesment_id") == "OT":

            assesment_data = OTAssesment.objects.filter(clienttable=k.id)
            html_string = render_to_string("OT_pdf.html", {"data": assesment_data,"client_data":data})
            html = HTML(string=html_string)

            html.write_pdf(target="/tmp/mypdf.pdf")
            fs = FileSystemStorage("/tmp")

            with fs.open("mypdf.pdf") as pdf:
                response = HttpResponse(pdf, content_type="application/pdf")
                print("response1", response)
                response["Content-Disposition"] = 'attachment; filename="mypdf.pdf"'
            return response

        if request.GET.get("assesment_id") == "ST":
            assesment_data = STAssesment.objects.filter(clienttable=k.id)
            html_string = render_to_string("ST_pdf.html", {"data": assesment_data,"client_data":data})
            html = HTML(string=html_string)

            html.write_pdf(target="/tmp/mypdf.pdf")
            fs = FileSystemStorage("/tmp")

            with fs.open("mypdf.pdf") as pdf:
                response = HttpResponse(pdf, content_type="application/pdf")
                print("response1", response)
                response["Content-Disposition"] = 'attachment; filename="mypdf.pdf"'

            return response
