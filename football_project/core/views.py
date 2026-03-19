from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from functools import wraps
from django.utils.http import url_has_allowed_host_and_scheme
from .models import *
from .forms import *

def get_user_role(u):
    if not u.is_authenticated: return None
    if u.is_superuser: return 'superuser'
    try:
        u.region_admin_profile; return 'region_admin'
    except: pass
    try:
        u.coach_profile; return 'coach'
    except: pass
    return None

def get_user_region(u):
    try: return u.region_admin_profile.region
    except: return None

def get_coach_team(u):
    try: return u.coach_profile.team
    except: return None

def any_staff(f):
    @wraps(f)
    def w(r,*a,**k):
        if not r.user.is_authenticated: return redirect('core:login')
        if not get_user_role(r.user): messages.error(r,"Ruxsat yo'q!"); return redirect('core:index')
        return f(r,*a,**k)
    return w

def superuser_required(f):
    @wraps(f)
    def w(r,*a,**k):
        if not r.user.is_authenticated: return redirect('core:login')
        if not r.user.is_superuser: messages.error(r,"Faqat sayt admini!"); return redirect('core:index')
        return f(r,*a,**k)
    return w

def superuser_or_radmin(f):
    @wraps(f)
    def w(r,*a,**k):
        if not r.user.is_authenticated: return redirect('core:login')
        role=get_user_role(r.user)
        if role not in('superuser','region_admin'): messages.error(r,"Ruxsat yo'q!"); return redirect('core:index')
        return f(r,*a,**k)
    return w

# === PUBLIC ===
def index(request):
    return render(request,'core/index.html',{
        'latest_news':News.objects.all()[:10],'latest_teams':Team.objects.all()[:4],
        'upcoming_competitions':Competition.objects.filter(date__gte=timezone.now().date(),date__lte=timezone.now().date()+timedelta(days=10),is_finished=False).order_by('date')[:5],
        'total_teams':Team.objects.count(),'total_players':Player.objects.count(),'total_competitions':Competition.objects.count(),'total_news':News.objects.count(),
    })

def login_view(request):
    if request.user.is_authenticated: return redirect('core:index')
    if request.method=='POST':
        form=LoginForm(request,data=request.POST)
        if form.is_valid():
            login(request,form.get_user()); messages.success(request,"Kirdingiz!")
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('core:index')
        else: messages.error(request,"Login yoki parol noto'g'ri!")
    else: form=LoginForm()
    return render(request,'auth/login.html',{'form':form})

def logout_view(request): logout(request); messages.success(request,"Chiqdingiz."); return redirect('core:index')
def news_list(request): return render(request,'news/list.html',{'news':Paginator(News.objects.all(),20).get_page(request.GET.get('page'))})
def news_detail(request,pk): a=get_object_or_404(News,pk=pk); return render(request,'news/detail.html',{'article':a,'photos':a.photos.all()})

def team_list(request):
    qs=Team.objects.select_related('city__region','category','coach').all()
    rid,cid,s=request.GET.get('region'),request.GET.get('category'),request.GET.get('search','')
    if rid: qs=qs.filter(city__region_id=rid)
    if cid: qs=qs.filter(category_id=cid)
    if s: qs=qs.filter(name__icontains=s)
    return render(request,'teams/list.html',{'teams':Paginator(qs,20).get_page(request.GET.get('page')),'regions':Region.objects.all(),'categories':Category.objects.all(),'selected_region':rid,'selected_category':cid,'search':s})

def team_detail(request,pk):
    team=get_object_or_404(Team.objects.select_related('coach','city__region','category'),pk=pk)
    return render(request,'teams/detail.html',{'team':team,'players_by_position':team.get_players_by_position()})

def competition_list(request):
    return render(request,'competitions/list.html',{'finished':Competition.objects.filter(is_finished=True).order_by('-date')[:10],'upcoming':Competition.objects.filter(date__gte=timezone.now().date(),is_finished=False).order_by('date')[:10]})

def competition_detail(request,pk):
    comp=get_object_or_404(Competition,pk=pk)
    matches=comp.matches.select_related('team_home','team_away').filter(is_bye=False) if comp.type=='round_robin' else comp.matches.select_related('team_home','team_away').all()
    return render(request,'competitions/detail.html',{'comp':comp,'matches':matches,'standings':comp.get_standings() if comp.type=='round_robin' else None,'olympic_rounds':comp.get_olympic_rounds() if comp.type=='olympic' else None})

def statistics(request): return render(request,'core/statistics.html')
def contact(request): return render(request,'core/contact.html')

def search_player(request):
    q=request.GET.get('q','').strip()
    if q:
        p=Player.objects.select_related('team','team__city__region').filter(player_id=q).first()
        if p: return render(request,'core/search_results.html',{'query':q,'player':p})
        ps=Player.objects.select_related('team').filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(player_id__icontains=q))[:10]
        if ps.exists(): return render(request,'core/search_results.html',{'query':q,'players':ps})
        return render(request,'core/search_results.html',{'query':q,'error':"Topilmadi"})
    return render(request,'core/search_results.html',{'query':q})

def player_id_card_pdf(request,pk):
    from reportlab.lib.units import mm; from reportlab.pdfgen import canvas as pc; from reportlab.lib.colors import HexColor,white,black
    from reportlab.graphics.barcode.qr import QrCodeWidget; from reportlab.graphics.shapes import Drawing; from reportlab.graphics import renderPDF
    from django.http import HttpResponse; import os
    player=get_object_or_404(Player.objects.select_related('team','team__city__region'),pk=pk)
    cw,ch=90*mm,57*mm; resp=HttpResponse(content_type='application/pdf')
    resp['Content-Disposition']=f'attachment; filename="ID_{player.player_id}_{player.last_name}.pdf"'
    c=pc.Canvas(resp,pagesize=(cw,ch)); gd,gm=HexColor('#15803d'),HexColor('#16a34a')
    c.setFillColor(gd);c.roundRect(0,ch-18*mm,cw,18*mm,0,fill=1,stroke=0);c.setFillColor(gm);c.roundRect(0,0,cw,9*mm,0,fill=1,stroke=0)
    c.setStrokeColor(gd);c.setLineWidth(1.5);c.roundRect(.5,.5,cw-1,ch-1,3*mm,fill=0,stroke=1)
    c.setFillColor(white);c.setFont("Helvetica-Bold",9);c.drawCentredString(cw/2,ch-8*mm,"O'ZBEKISTON FUTBOL");c.setFont("Helvetica-Bold",8);c.drawCentredString(cw/2,ch-12.5*mm,"ASSOTSIATSIYASI")
    px,py,pw,ph=5*mm,12*mm,22*mm,26*mm;c.setFillColor(HexColor('#f0fdf4'));c.setStrokeColor(gm);c.setLineWidth(1);c.roundRect(px,py,pw,ph,2*mm,fill=1,stroke=1)
    if player.photo:
        try:
            if os.path.exists(player.photo.path):c.drawImage(player.photo.path,px+mm,py+mm,pw-2*mm,ph-2*mm,preserveAspectRatio=True,mask='auto')
        except:pass
    else:c.setFillColor(HexColor('#86efac'));c.setFont("Helvetica-Bold",14);c.drawCentredString(px+pw/2,py+ph/2,f"{player.first_name[0]}{player.last_name[0]}")
    ix=30*mm;c.setFillColor(black);c.setFont("Helvetica-Bold",10);c.drawString(ix,ch-22*mm,f"{player.first_name} {player.last_name}")
    c.setFont("Helvetica",7.5);c.setFillColor(HexColor('#4b5563'));c.drawString(ix,ch-26.5*mm,player.birthday.strftime('%d/%m/%Y'))
    tt=player.team.name+(f" ({player.team.city.region.name})" if player.team.city and player.team.city.region else "");c.drawString(ix,ch-31*mm,tt)
    c.setFont("Helvetica-Bold",7.5);c.setFillColor(gd);c.drawString(ix,ch-35.5*mm,f"Pozitsiya: {player.get_position_display()}")
    c.setFont("Helvetica-Bold",9);c.setFillColor(HexColor('#dc2626'));c.drawString(ix,ch-41*mm,f"ID: {player.player_id}")
    qr=QrCodeWidget(f"ID:{player.player_id}");qr.barWidth=qr.barHeight=15*mm;d=Drawing(15*mm,15*mm);d.add(qr);renderPDF.draw(d,c,cw-22*mm,12*mm)
    c.setFillColor(white);c.setFont("Helvetica-Bold",8);c.drawCentredString(cw/2,3*mm,"www.e-futbol.uz");c.save();return resp

# === ADMIN PANEL ===
@any_staff
def admin_dashboard(request):
    role=get_user_role(request.user);region=get_user_region(request.user);ct=get_coach_team(request.user)
    ctx={'role':role,'coach_team':ct,'region':region}
    if role=='superuser': ctx.update({'total_teams':Team.objects.count(),'total_players':Player.objects.count(),'total_competitions':Competition.objects.count(),'total_news':News.objects.count(),'pending_requests':PlayerRequest.objects.filter(status='pending').count()})
    elif role=='region_admin':
        rt=Team.objects.filter(city__region=region);ctx.update({'total_teams':rt.count(),'total_players':Player.objects.filter(team__in=rt).count(),'total_competitions':Competition.objects.filter(stadium__city__region=region).count(),'pending_requests':PlayerRequest.objects.filter(team__city__region=region,status='pending').count()})
    elif role=='coach' and ct: ctx.update({'total_players':ct.players.count(),'my_requests':PlayerRequest.objects.filter(created_by=request.user).count(),'pending_requests':PlayerRequest.objects.filter(created_by=request.user,status='pending').count()})
    return render(request,'admin_panel/dashboard.html',ctx)

# NEWS
@superuser_required
def admin_news_list(request): return render(request,'admin_panel/news_list.html',{'news':News.objects.all()})
@superuser_required
def admin_news_create(request):
    if request.method=='POST':
        form=NewsForm(request.POST)
        if form.is_valid():
            a=form.save(commit=False);a.created_by=request.user;a.save()
            for f in request.FILES.getlist('photos'):NewsPhoto.objects.create(news=a,file=f)
            messages.success(request,"Yaratildi!");return redirect('core:admin_news_list')
    else:form=NewsForm()
    return render(request,'admin_panel/news_form.html',{'form':form,'title':"Yangilik yaratish"})
@superuser_required
def admin_news_edit(request,pk):
    a=get_object_or_404(News,pk=pk)
    if request.method=='POST':
        form=NewsForm(request.POST,instance=a)
        if form.is_valid():
            form.save();[NewsPhoto.objects.create(news=a,file=f) for f in request.FILES.getlist('photos')]
            messages.success(request,"Yangilandi!");return redirect('core:admin_news_list')
    else:form=NewsForm(instance=a)
    return render(request,'admin_panel/news_form.html',{'form':form,'article':a,'title':"Tahrirlash"})
@superuser_required
def admin_news_delete(request,pk):
    if request.method=='POST':get_object_or_404(News,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_news_list')

# TEAMS
@any_staff
def admin_team_list(request):
    role=get_user_role(request.user)
    if role=='superuser':teams=Team.objects.all()
    elif role=='region_admin':teams=Team.objects.filter(city__region=get_user_region(request.user))
    else:ct=get_coach_team(request.user);teams=Team.objects.filter(pk=ct.pk) if ct else Team.objects.none()
    return render(request,'admin_panel/team_list.html',{'teams':teams})
@superuser_or_radmin
def admin_team_create(request):
    role=get_user_role(request.user);region=get_user_region(request.user)
    if request.method=='POST':
        form=TeamForm(request.POST,request.FILES)
        if form.is_valid():
            t=form.save(commit=False)
            if role=='region_admin' and t.city.region!=region:messages.error(request,"Faqat o'z viloyatingizda!");return redirect('core:admin_team_list')
            t.save();messages.success(request,"Yaratildi!");return redirect('core:admin_team_list')
    else:
        form=TeamForm()
        if role=='region_admin':form.fields['city'].queryset=City.objects.filter(region=region)
    return render(request,'admin_panel/team_form.html',{'form':form,'title':"Jamoa yaratish"})
@superuser_or_radmin
def admin_team_edit(request,pk):
    team=get_object_or_404(Team,pk=pk);role=get_user_role(request.user);region=get_user_region(request.user)
    if role=='region_admin' and team.city.region!=region:messages.error(request,"Sizning viloyatingiz emas!");return redirect('core:admin_team_list')
    if request.method=='POST':
        form=TeamForm(request.POST,request.FILES,instance=team)
        if form.is_valid():form.save();messages.success(request,"Yangilandi!");return redirect('core:admin_team_list')
    else:
        form=TeamForm(instance=team)
        if role=='region_admin':form.fields['city'].queryset=City.objects.filter(region=region)
    return render(request,'admin_panel/team_form.html',{'form':form,'team':team,'title':"Tahrirlash"})
@superuser_required
def admin_team_delete(request,pk):
    if request.method=='POST':get_object_or_404(Team,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_team_list')

# PLAYERS
@any_staff
def admin_player_list(request):
    role=get_user_role(request.user)
    if role=='superuser':players=Player.objects.select_related('team').all()
    elif role=='region_admin':players=Player.objects.filter(team__city__region=get_user_region(request.user))
    else:ct=get_coach_team(request.user);players=Player.objects.filter(team=ct) if ct else Player.objects.none()
    return render(request,'admin_panel/player_list.html',{'players':players})
@superuser_or_radmin
def admin_player_create(request):
    role=get_user_role(request.user);region=get_user_region(request.user)
    if request.method=='POST':
        form=PlayerForm(request.POST,request.FILES)
        if form.is_valid():form.save();messages.success(request,"Qo'shildi!");return redirect('core:admin_player_list')
    else:
        form=PlayerForm()
        if role=='region_admin':form.fields['team'].queryset=Team.objects.filter(city__region=region)
    return render(request,'admin_panel/player_form.html',{'form':form,'title':"O'yinchi qo'shish"})
@superuser_or_radmin
def admin_player_edit(request,pk):
    p=get_object_or_404(Player,pk=pk)
    if request.method=='POST':
        form=PlayerForm(request.POST,request.FILES,instance=p)
        if form.is_valid():form.save();messages.success(request,"Yangilandi!");return redirect('core:admin_player_list')
    else:form=PlayerForm(instance=p)
    return render(request,'admin_panel/player_form.html',{'form':form,'player':p,'title':"Tahrirlash"})
@superuser_or_radmin
def admin_player_delete(request,pk):
    if request.method=='POST':get_object_or_404(Player,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_player_list')

# PLAYER REQUESTS
@any_staff
def admin_player_requests(request):
    role=get_user_role(request.user)
    if role=='superuser':reqs=PlayerRequest.objects.select_related('team','created_by').all()
    elif role=='region_admin':reqs=PlayerRequest.objects.filter(team__city__region=get_user_region(request.user))
    elif role=='coach':reqs=PlayerRequest.objects.filter(created_by=request.user)
    else:reqs=PlayerRequest.objects.none()
    return render(request,'admin_panel/player_requests.html',{'requests':reqs,'role':role})

@any_staff
def admin_player_request_create(request):
    ct=get_coach_team(request.user)
    if not ct:messages.error(request,"Sizda jamoa yo'q!");return redirect('core:admin_dashboard')
    if request.method=='POST':
        form=PlayerRequestForm(request.POST,request.FILES)
        if form.is_valid():pr=form.save(commit=False);pr.team=ct;pr.created_by=request.user;pr.save();messages.success(request,"So'rov yuborildi!");return redirect('core:admin_player_requests')
    else:form=PlayerRequestForm()
    return render(request,'admin_panel/player_request_form.html',{'form':form,'title':"Yangi o'yinchi so'rovi"})

@superuser_or_radmin
def admin_player_request_review(request,pk):
    pr=get_object_or_404(PlayerRequest,pk=pk);role=get_user_role(request.user)
    if role=='region_admin' and pr.team.city.region!=get_user_region(request.user):messages.error(request,"Sizning viloyatingiz emas!");return redirect('core:admin_player_requests')
    if request.method=='POST':
        action=request.POST.get('action');form=PlayerRequestEditForm(request.POST,request.FILES,instance=pr)
        if action=='approve' and form.is_valid():form.save();pr.refresh_from_db();p=pr.approve();messages.success(request,f"Tasdiqlandi! ID:{p.player_id}");return redirect('core:admin_player_requests')
        elif action=='reject':
            if form.is_valid():form.save()
            pr.reject(note=request.POST.get('admin_note',''));messages.success(request,"Rad etildi.");return redirect('core:admin_player_requests')
    else:form=PlayerRequestEditForm(instance=pr)
    return render(request,'admin_panel/player_request_review.html',{'form':form,'pr':pr,'title':"So'rovni ko'rish"})

# COMPETITIONS
@superuser_or_radmin
def admin_competition_list(request):
    role=get_user_role(request.user)
    comps=Competition.objects.all() if role=='superuser' else Competition.objects.filter(stadium__city__region=get_user_region(request.user))
    return render(request,'admin_panel/competition_list.html',{'competitions':comps})
@superuser_or_radmin
def admin_competition_create(request):
    role=get_user_role(request.user);region=get_user_region(request.user);kw={'region':region} if role=='region_admin' else {}
    if request.method=='POST':
        form=CompetitionForm(request.POST,**kw)
        if form.is_valid():comp=form.save(commit=False);comp.created_by=request.user;comp.save();form.save_m2m();messages.success(request,"Yaratildi!");return redirect('core:admin_competition_list')
    else:form=CompetitionForm(**kw)
    return render(request,'admin_panel/competition_form.html',{'form':form,'title':"Musobaqa yaratish"})
@superuser_or_radmin
def admin_competition_edit(request,pk):
    comp=get_object_or_404(Competition,pk=pk);role=get_user_role(request.user);region=get_user_region(request.user);kw={'region':region} if role=='region_admin' else {}
    if request.method=='POST':
        form=CompetitionForm(request.POST,instance=comp,**kw)
        if form.is_valid():form.save();messages.success(request,"Yangilandi!");return redirect('core:admin_competition_list')
    else:form=CompetitionForm(instance=comp,**kw)
    return render(request,'admin_panel/competition_form.html',{'form':form,'comp':comp,'title':"Tahrirlash"})
@superuser_or_radmin
def admin_competition_draw(request,pk):
    comp=get_object_or_404(Competition,pk=pk)
    if request.method=='POST' and not comp.draw_done:comp.generate_draw();messages.success(request,"Qur'a tashlandi!")
    return redirect('core:admin_competition_scores',pk=pk)
@superuser_or_radmin
def admin_competition_scores(request,pk):
    comp=get_object_or_404(Competition,pk=pk);matches=comp.matches.select_related('team_home','team_away').order_by('round_number')
    if request.method=='POST':
        for m in matches:
            if m.is_bye:continue
            sh,sa,fin=request.POST.get(f'score_home_{m.id}'),request.POST.get(f'score_away_{m.id}'),request.POST.get(f'finished_{m.id}')
            if sh is not None and sa is not None:
                sh = (sh or '').strip()
                sa = (sa or '').strip()
                is_finished = fin == 'on'
                try:
                    if sh == '' and sa == '':
                        m.score_home = None
                        m.score_away = None
                        m.is_finished = False
                    elif sh.isdigit() and sa.isdigit():
                        m.score_home = int(sh)
                        m.score_away = int(sa)
                        m.is_finished = is_finished
                    else:
                        continue
                    m.save()
                except Exception:
                    continue
        messages.success(request,"Saqlandi!");return redirect('core:admin_competition_scores',pk=pk)
    return render(request,'admin_panel/competition_scores.html',{'comp':comp,'matches':matches})
@superuser_or_radmin
def admin_competition_finish(request,pk):
    comp=get_object_or_404(Competition,pk=pk)
    if request.method=='POST':comp.is_finished=True;comp.save();messages.success(request,"Yakunlandi!")
    return redirect('core:admin_competition_list')
@superuser_or_radmin
def admin_competition_next_round(request,pk):
    comp=get_object_or_404(Competition,pk=pk)
    if comp.type!='olympic' or comp.is_finished:return redirect('core:admin_competition_scores',pk=pk)
    if request.method=='POST':
        rounds=comp.get_olympic_rounds()
        if not rounds:return redirect('core:admin_competition_scores',pk=pk)
        lr=max(rounds.keys());lm=rounds[lr]
        if not all(m.is_finished for m in lm):messages.error(request,"Oldingi raund yakunlanmagan!");return redirect('core:admin_competition_scores',pk=pk)
        winners=[m.get_winner() for m in lm if m.get_winner()]
        if len(winners)<2:comp.is_finished=True;comp.save();messages.info(request,"Yakunlangan!");return redirect('core:admin_competition_scores',pk=pk)
        nr=lr+1;i=0
        while i<len(winners)-1:Match.objects.create(competition=comp,team_home=winners[i],team_away=winners[i+1],round_number=nr);i+=2
        if len(winners)%2==1:Match.objects.create(competition=comp,team_home=winners[-1],team_away=winners[-1],round_number=nr,score_home=0,score_away=0,is_finished=True,is_bye=True)
        messages.success(request,f"{nr}-raund yaratildi!")
    return redirect('core:admin_competition_scores',pk=pk)

# TRANSFERS
@any_staff
def admin_transfers(request):
    role=get_user_role(request.user);ct=get_coach_team(request.user)
    if role=='superuser':inc=TransferRequest.objects.all();out=TransferRequest.objects.none()
    elif role=='coach' and ct:inc=TransferRequest.objects.filter(to_team=ct);out=TransferRequest.objects.filter(from_team=ct)
    else:inc=out=TransferRequest.objects.none()
    return render(request,'admin_panel/transfers.html',{'incoming':inc,'outgoing':out,'coach_team':ct})
@any_staff
def admin_transfer_create(request):
    ct=get_coach_team(request.user)
    if not ct:messages.error(request,"Jamoa yo'q!");return redirect('core:admin_transfers')
    if request.method=='POST':
        form=TransferRequestForm(request.POST,team=ct)
        if form.is_valid():TransferRequest.objects.create(player=form.cleaned_data['player'],from_team=ct,to_team=form.cleaned_data['to_team'],message=form.cleaned_data.get('message',''));messages.success(request,"Yuborildi!");return redirect('core:admin_transfers')
    else:form=TransferRequestForm(team=ct)
    return render(request,'admin_panel/transfer_form.html',{'form':form})
@any_staff
def admin_transfer_accept(request,pk):
    t=get_object_or_404(TransferRequest,pk=pk);ct=get_coach_team(request.user)
    if request.user.is_superuser or(ct and t.to_team==ct):
        if request.method=='POST' and t.status=='pending':t.accept();messages.success(request,"Qabul qilindi!")
    return redirect('core:admin_transfers')
@any_staff
def admin_transfer_reject(request,pk):
    t=get_object_or_404(TransferRequest,pk=pk);ct=get_coach_team(request.user)
    if request.user.is_superuser or(ct and t.to_team==ct):
        if request.method=='POST' and t.status=='pending':t.reject();messages.success(request,"Rad etildi.")
    return redirect('core:admin_transfers')

# GENERIC CRUD (superuser only)
@superuser_required
def admin_regions(request): return render(request,'admin_panel/generic_list.html',{'items':Region.objects.all(),'title':'Viloyatlar','create_url':'core:admin_region_create','edit_url':'core:admin_region_edit','delete_url':'core:admin_region_delete'})
@superuser_required
def admin_region_create(request):
    if request.method=='POST':
        f=RegionForm(request.POST)
        if f.is_valid():
            f.save();messages.success(request,"Yaratildi!");return redirect('core:admin_regions')
    else:f=RegionForm()
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Viloyat qo'shish"})
@superuser_required
def admin_region_edit(request,pk):
    o=get_object_or_404(Region,pk=pk)
    if request.method=='POST':
        f=RegionForm(request.POST,instance=o)
        if f.is_valid():
            f.save();messages.success(request,"Yangilandi!");return redirect('core:admin_regions')
    else:f=RegionForm(instance=o)
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Tahrirlash"})
@superuser_required
def admin_region_delete(request,pk):
    if request.method=='POST':get_object_or_404(Region,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_regions')
@superuser_required
def admin_cities(request): return render(request,'admin_panel/generic_list.html',{'items':City.objects.select_related('region').all(),'title':'Shaharlar','create_url':'core:admin_city_create','edit_url':'core:admin_city_edit','delete_url':'core:admin_city_delete'})
@superuser_required
def admin_city_create(request):
    if request.method=='POST':
        f=CityForm(request.POST)
        if f.is_valid():
            f.save();messages.success(request,"Yaratildi!");return redirect('core:admin_cities')
    else:f=CityForm()
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Shahar qo'shish"})
@superuser_required
def admin_city_edit(request,pk):
    o=get_object_or_404(City,pk=pk)
    if request.method=='POST':
        f=CityForm(request.POST,instance=o)
        if f.is_valid():
            f.save();messages.success(request,"Yangilandi!");return redirect('core:admin_cities')
    else:f=CityForm(instance=o)
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Tahrirlash"})
@superuser_required
def admin_city_delete(request,pk):
    if request.method=='POST':get_object_or_404(City,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_cities')
@superuser_required
def admin_categories(request): return render(request,'admin_panel/generic_list.html',{'items':Category.objects.all(),'title':'Kategoriyalar','create_url':'core:admin_category_create','edit_url':'core:admin_category_edit','delete_url':'core:admin_category_delete'})
@superuser_required
def admin_category_create(request):
    if request.method=='POST':
        f=CategoryForm(request.POST)
        if f.is_valid():
            f.save();messages.success(request,"Yaratildi!");return redirect('core:admin_categories')
    else:f=CategoryForm()
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Kategoriya qo'shish"})
@superuser_required
def admin_category_edit(request,pk):
    o=get_object_or_404(Category,pk=pk)
    if request.method=='POST':
        f=CategoryForm(request.POST,instance=o)
        if f.is_valid():
            f.save();messages.success(request,"Yangilandi!");return redirect('core:admin_categories')
    else:f=CategoryForm(instance=o)
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Tahrirlash"})
@superuser_required
def admin_category_delete(request,pk):
    if request.method=='POST':get_object_or_404(Category,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_categories')

# COACHES
@superuser_or_radmin
def admin_coaches(request):
    role=get_user_role(request.user)
    items=Coach.objects.all() if role=='superuser' else Coach.objects.filter(team__city__region=get_user_region(request.user))
    return render(request,'admin_panel/coach_list.html',{'coaches':items})
@superuser_or_radmin
def admin_coach_create(request):
    role=get_user_role(request.user);region=get_user_region(request.user)
    if request.method=='POST':
        form=CoachCreateForm(request.POST,request.FILES,region=region if role=='region_admin' else None)
        if form.is_valid():
            un=form.cleaned_data['username']
            if User.objects.filter(username=un).exists():messages.error(request,f"'{un}' mavjud!")
            else:
                u=User.objects.create_user(username=un,password=form.cleaned_data['password'])
                coach=Coach.objects.create(user=u,first_name=form.cleaned_data['first_name'],last_name=form.cleaned_data['last_name'],fathers_name=form.cleaned_data.get('fathers_name',''),photo=form.cleaned_data.get('photo'))
                team=form.cleaned_data.get('team')
                if team:team.coach=coach;team.save()
                messages.success(request,f"Yaratildi! Login:{un}");return redirect('core:admin_coaches')
    else:form=CoachCreateForm(region=region if role=='region_admin' else None)
    return render(request,'admin_panel/coach_form.html',{'form':form,'title':"Murabbiy yaratish"})
@superuser_or_radmin
def admin_coach_delete(request,pk):
    c=get_object_or_404(Coach,pk=pk)
    if request.method=='POST':
        if c.user:c.user.delete()
        c.delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_coaches')

# REGION ADMINS (superuser only)
@superuser_required
def admin_region_admins(request):
    return render(request,'admin_panel/region_admin_list.html',{'region_admins':RegionAdmin.objects.select_related('user','region').all()})
@superuser_required
def admin_region_admin_create(request):
    if request.method=='POST':
        form=RegionAdminForm(request.POST);un,pw=request.POST.get('username',''),request.POST.get('password','')
        if form.is_valid():
            if User.objects.filter(username=un).exists():messages.error(request,f"'{un}' mavjud!")
            else:
                u=User.objects.create_user(username=un,password=pw);ra=form.save(commit=False);ra.user=u;ra.save()
                messages.success(request,f"Yaratildi! Login:{un}");return redirect('core:admin_region_admins')
    else:form=RegionAdminForm()
    return render(request,'admin_panel/region_admin_form.html',{'form':form,'title':"Viloyat admini tayinlash"})
@superuser_required
def admin_region_admin_delete(request,pk):
    ra=get_object_or_404(RegionAdmin,pk=pk)
    if request.method=='POST':
        if ra.user:ra.user.delete()
        ra.delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_region_admins')

# STADIUMS
@superuser_or_radmin
def admin_stadiums(request):
    role=get_user_role(request.user)
    items=Stadium.objects.all() if role=='superuser' else Stadium.objects.filter(city__region=get_user_region(request.user))
    return render(request,'admin_panel/generic_list.html',{'items':items,'title':'Stadionlar','create_url':'core:admin_stadium_create','edit_url':'core:admin_stadium_edit','delete_url':'core:admin_stadium_delete'})
@superuser_or_radmin
def admin_stadium_create(request):
    role=get_user_role(request.user);region=get_user_region(request.user)
    if request.method=='POST':
        f=StadiumForm(request.POST,region=region if role=='region_admin' else None)
        if f.is_valid():f.save();messages.success(request,"Yaratildi!");return redirect('core:admin_stadiums')
    else:f=StadiumForm(region=region if role=='region_admin' else None)
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Stadion qo'shish"})
@superuser_or_radmin
def admin_stadium_edit(request,pk):
    o=get_object_or_404(Stadium,pk=pk);role=get_user_role(request.user);region=get_user_region(request.user)
    if request.method=='POST':
        f=StadiumForm(request.POST,instance=o,region=region if role=='region_admin' else None)
        if f.is_valid():f.save();messages.success(request,"Yangilandi!");return redirect('core:admin_stadiums')
    else:f=StadiumForm(instance=o,region=region if role=='region_admin' else None)
    return render(request,'admin_panel/generic_form.html',{'form':f,'title':"Tahrirlash"})
@superuser_or_radmin
def admin_stadium_delete(request,pk):
    if request.method=='POST':get_object_or_404(Stadium,pk=pk).delete();messages.success(request,"O'chirildi!")
    return redirect('core:admin_stadiums')